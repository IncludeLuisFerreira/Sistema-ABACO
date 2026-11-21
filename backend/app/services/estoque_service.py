from datetime import datetime

from fastapi import BackgroundTasks
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.email.messages import ItemEstoqueBaixo
from app.models.estoque import Estoque
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.pedido import Pedido
from app.schemas.estoque_schema import EstoqueCreateSchema, EstoqueUpdateSchema
from app.services.notificacao_eventos_service import (
    itens_recem_baixos,
    notificar_estoque_baixo,
    snapshot_estoque,
)
from app.services.pedido_service import (
    EstoqueNotFoundForPedidoError,
    PedidoItemInvalidoError,
)


class EstoqueNotFoundError(Exception):
    pass


class EstoqueHasDependenciesError(Exception):
    pass


class EstoqueSaldoInsuficienteError(Exception):
    pass


class EstoqueBaixaJustificativaError(Exception):
    pass


class EstoqueAlreadyExistsError(Exception):
    pass


def _is_unique_violation(exc: IntegrityError) -> bool:
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)
    if pgcode == "23505":
        return True
    message = str(orig or exc).lower()
    return "unique" in message or "uq_estoque_nomeitem_lower" in message


def create_estoque(db: Session, payload: EstoqueCreateSchema, background_tasks: BackgroundTasks | None = None) -> Estoque:
    existing = db.query(Estoque).filter(
        func.lower(Estoque.nome_item) == func.lower(payload.nomeItem.strip())
    ).first()

    if existing:
        raise EstoqueAlreadyExistsError(
            f"Item '{payload.nomeItem}' já existe no estoque. Use o endpoint de atualização para modificar a quantidade."
        )

    estoque = Estoque(
        nome_item=payload.nomeItem.strip(),
        quantidade_disponivel=payload.quantidadeDisponivel,
        unidade=payload.unidade,
        estoque_minimo=payload.estoqueMinimo,
    )
    db.add(estoque)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EstoqueAlreadyExistsError(
            f"Item '{payload.nomeItem}' já existe no estoque. Use o endpoint de atualização para modificar a quantidade."
        ) from exc
    db.refresh(estoque)
    notificar_estoque_baixo(db, itens_recem_baixos({}, [estoque]), background_tasks)
    return estoque


def list_estoque(db: Session) -> list[Estoque]:
    return db.query(Estoque).order_by(Estoque.nome_item).all()


def search_estoque_by_name(db: Session, term: str) -> list[Estoque]:
    return db.query(Estoque).filter(
        Estoque.nome_item.ilike(f"%{term}%")
    ).order_by(Estoque.nome_item).all()


def get_estoque_by_id(db: Session, estoque_id: int) -> Estoque:
    estoque = db.query(Estoque).filter(Estoque.id_item_estoque == estoque_id).first()
    if not estoque:
        raise EstoqueNotFoundError
    return estoque


def update_estoque(db: Session, estoque_id: int, payload: EstoqueUpdateSchema, background_tasks: BackgroundTasks | None = None) -> Estoque:
    estoque = get_estoque_by_id(db, estoque_id)
    anteriores = {estoque.id_item_estoque: snapshot_estoque(estoque)}

    if payload.nomeItem is not None:
        estoque.nome_item = payload.nomeItem
    if payload.quantidadeDisponivel is not None:
        estoque.quantidade_disponivel = payload.quantidadeDisponivel
    if payload.unidade is not None:
        estoque.unidade = payload.unidade
    if payload.estoqueMinimo is not None:
        estoque.estoque_minimo = payload.estoqueMinimo

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_unique_violation(exc):
            raise EstoqueAlreadyExistsError(
                f"Item '{estoque.nome_item}' já existe no estoque. Use o endpoint de atualização para modificar a quantidade."
            ) from exc
        raise EstoqueHasDependenciesError from exc

    db.refresh(estoque)
    notificar_estoque_baixo(db, itens_recem_baixos(anteriores, [estoque]), background_tasks)
    return estoque


def delete_estoque(db: Session, estoque_id: int) -> None:
    estoque = get_estoque_by_id(db, estoque_id)
    db.delete(estoque)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EstoqueHasDependenciesError from exc


def dar_baixa(db: Session, estoque_id: int, quantidade: int, justificativa: str, background_tasks: BackgroundTasks | None = None) -> Estoque:
    estoque = get_estoque_by_id(db, estoque_id)
    anteriores = {estoque.id_item_estoque: snapshot_estoque(estoque)}

    saldo_atual = estoque.quantidade_disponivel or 0
    if saldo_atual < quantidade:
        raise EstoqueSaldoInsuficienteError(
            f"Saldo insuficiente. Disponível: {saldo_atual}, solicitado: {quantidade}"
        )

    estoque.quantidade_disponivel = saldo_atual - quantidade

    movimentacao = MovimentacaoEstoque(
        id_item_estoque=estoque_id,
        quantidade=-quantidade,
        tipo_movimentacao="baixa_manual",
        justificativa=justificativa,
        data_movimentacao=datetime.now(),
    )
    db.add(movimentacao)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EstoqueHasDependenciesError from exc

    db.refresh(estoque)
    notificar_estoque_baixo(db, itens_recem_baixos(anteriores, [estoque]), background_tasks)
    return estoque


def get_alertas(db: Session) -> list[Estoque]:
    return (
        db.query(Estoque)
        .filter(
            Estoque.quantidade_disponivel <= Estoque.estoque_minimo,
            Estoque.estoque_minimo.isnot(None),
        )
        .order_by(Estoque.nome_item)
        .all()
    )


def deduzir_por_pedido(db: Session, pedido: Pedido) -> list[ItemEstoqueBaixo]:
    # HACK: with_for_update não funciona em SQLite e o rollback fica a cargo do caller
    from app.models.item_pedido import ItemPedido

    itens: list[ItemPedido] = pedido.itens or []
    anteriores: dict[int, ItemEstoqueBaixo | None] = {}
    alterados: list[Estoque] = []
    ids_alterados: set[int] = set()

    for item in itens:
        if item.id_item_estoque is None or item.quantidade is None or item.quantidade <= 0:
            raise PedidoItemInvalidoError(
                "Itens do pedido precisam ter estoque vinculado e quantidade maior que zero"
            )

        estoque_item = (
            db.query(Estoque)
            .filter(Estoque.id_item_estoque == item.id_item_estoque)
            .with_for_update()
            .first()
        )

        if not estoque_item:
            raise EstoqueNotFoundForPedidoError(
                f"Item de estoque {item.id_item_estoque} não encontrado"
            )

        # Preserva o estado original do primeiro item com esse estoque e evita
        # duplicar o mesmo item no alerta quando o pedido tem linhas repetidas.
        anteriores.setdefault(estoque_item.id_item_estoque, snapshot_estoque(estoque_item))
        if estoque_item.id_item_estoque not in ids_alterados:
            alterados.append(estoque_item)
            ids_alterados.add(estoque_item.id_item_estoque)

        saldo_atual = estoque_item.quantidade_disponivel or 0
        if saldo_atual < item.quantidade:
            raise EstoqueSaldoInsuficienteError(
                f"Saldo insuficiente para '{estoque_item.nome_item}'. "
                f"Disponível: {saldo_atual}, solicitado: {item.quantidade}"
            )

        estoque_item.quantidade_disponivel = saldo_atual - item.quantidade

        movimentacao = MovimentacaoEstoque(
            id_item_estoque=item.id_item_estoque,
            quantidade=-item.quantidade,
            tipo_movimentacao="pedido_aprovado",
            justificativa=f"Pedido #{pedido.id_pedido} - {estoque_item.nome_item or item.nome_item}",
            data_movimentacao=datetime.now(),
        )
        db.add(movimentacao)

    return itens_recem_baixos(anteriores, alterados)
