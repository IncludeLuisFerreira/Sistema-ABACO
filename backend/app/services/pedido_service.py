from datetime import date

from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.email.messages import ItemEstoqueBaixo
from app.models.estoque import Estoque
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.schemas.pedido_schema import PedidoCompraSchema, PedidoCreateSchema, PedidoUpdateSchema
from app.services import notificacao_eventos_service as notificacoes_eventos


class PedidoNotFoundError(Exception):
    pass


class PedidoHasDependenciesError(Exception):
    pass


class TurmaNotFoundForPedidoError(Exception):
    pass


class EstoqueNotFoundForPedidoError(Exception):
    pass


class PedidoItemInvalidoError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class PedidoCannotBeDeliveredError(Exception):
    pass


class PedidoInvalidTransitionError(Exception):
    pass


def _resolve_turma(db: Session, turma_id: int) -> None:
    from app.models.turma import Turma

    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundForPedidoError


def _resolve_estoque(db: Session, estoque_id: int) -> Estoque:
    estoque_item = (
        db.query(Estoque).filter(Estoque.id_item_estoque == estoque_id).first()
    )
    if not estoque_item:
        raise EstoqueNotFoundForPedidoError(
            f"Item de estoque {estoque_id} não encontrado"
        )
    return estoque_item


def create_pedido(db: Session, payload: PedidoCreateSchema, usuario_id: int) -> Pedido:
    _resolve_turma(db, payload.idTurma)
    # Valida todos os itens antes de gravar qualquer coisa: id inexistente vira 400.
    for item in payload.itens:
        _resolve_estoque(db, item.idItemEstoque)

    pedido = Pedido(
        id_usuario=usuario_id,
        id_turma=payload.idTurma,
        data_pedido=payload.dataPedido or date.today(),
        status=0,
    )

    try:
        db.add(pedido)
        db.flush()

        for item in payload.itens:
            item_pedido = ItemPedido(
                id_pedido=pedido.id_pedido,
                nome_item=item.nomeItem,
                id_item_estoque=item.idItemEstoque,
                quantidade=item.quantidade,
                preco_unitario=item.precoUnitario,
            )
            db.add(item_pedido)

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc

    db.refresh(pedido)
    notificacoes_eventos.notificar_pedido_criado(db, pedido, usuario_id)
    return pedido


def list_pedidos(db: Session, solicitante_id: int | None = None) -> list[Pedido]:
    query = db.query(Pedido)
    if solicitante_id is not None:
        query = query.filter(Pedido.id_usuario == solicitante_id)
    return query.order_by(Pedido.id_pedido.desc()).all()


def get_pedido_by_id(db: Session, pedido_id: int, solicitante_id: int | None = None) -> Pedido:
    query = db.query(Pedido).filter(Pedido.id_pedido == pedido_id)
    if solicitante_id is not None:
        # Pedido de terceiro é tratado como inexistente para não revelar a existência.
        query = query.filter(Pedido.id_usuario == solicitante_id)
    pedido = query.first()
    if not pedido:
        raise PedidoNotFoundError
    return pedido


def _aprovar_pedido(
    db: Session,
    pedido: Pedido,
    background_tasks: BackgroundTasks | None = None,
) -> Pedido:
    from app.services.estoque_service import EstoqueSaldoInsuficienteError, deduzir_por_pedido

    if pedido.status != 0:
        raise PedidoInvalidTransitionError("Apenas pedidos com status 'Solicitado' podem ser aprovados")

    pedido.status = 1
    itens_baixos: list[ItemEstoqueBaixo] = []

    try:
        itens_baixos = deduzir_por_pedido(db, pedido)
        db.commit()
    except (
        EstoqueSaldoInsuficienteError,
        EstoqueNotFoundForPedidoError,
        PedidoItemInvalidoError,
    ) as exc:
        db.rollback()
        raise PedidoInvalidTransitionError(str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc

    db.refresh(pedido)
    # Inbox e e-mail passam pelo dispatcher, após o commit, sem reverter a aprovação.
    notificacoes_eventos.notificar_pedido_aprovado(db, pedido, background_tasks)
    notificacoes_eventos.notificar_estoque_baixo(db, itens_baixos, background_tasks)
    return pedido


def aprovar_pedido(
    db: Session,
    pedido_id: int,
    background_tasks: BackgroundTasks | None = None,
) -> Pedido:
    pedido = get_pedido_by_id(db, pedido_id)
    return _aprovar_pedido(db, pedido, background_tasks)


def comprar_pedido(db: Session, pedido_id: int, payload: PedidoCompraSchema, background_tasks: BackgroundTasks | None = None) -> Pedido:
    pedido = get_pedido_by_id(db, pedido_id)

    if pedido.status != 1:
        raise PedidoInvalidTransitionError("Apenas pedidos com status 'Aprovado' podem ser marcados como comprados")

    qtd_map = {item.idItemPedido: item.quantidade for item in payload.itens}
    itens_por_id = {item.id_item_pedido: item for item in pedido.itens}

    # A baixa do estoque acontece na aprovação. Alterar a quantidade depois
    # disso deixaria o saldo e a auditoria inconsistentes.
    for item_id, quantidade in qtd_map.items():
        item_pedido = itens_por_id.get(item_id)
        if item_pedido is None:
            raise PedidoInvalidTransitionError(
                f"Item {item_id} não pertence ao pedido"
            )
        if item_pedido.quantidade != quantidade:
            raise PedidoInvalidTransitionError(
                "A quantidade dos itens não pode ser alterada após a aprovação"
            )

    pedido.status = 2

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc

    db.refresh(pedido)
    notificacoes_eventos.notificar_pedido_comprado(db, pedido)
    return pedido


def update_pedido_status(
    db: Session,
    pedido_id: int,
    payload: PedidoUpdateSchema,
    background_tasks: BackgroundTasks | None = None,
) -> Pedido:
    pedido = get_pedido_by_id(db, pedido_id)

    if payload.status not in (1, 2):
        raise PedidoInvalidTransitionError(
            "Transição de status inválida. Use os endpoints específicos para aprovar, comprar ou entregar."
        )

    # Aprovação deve passar exatamente pelo mesmo fluxo do endpoint /aprovar.
    if payload.status == 1:
        return _aprovar_pedido(db, pedido, background_tasks)

    if pedido.status != 1:
        raise PedidoInvalidTransitionError(
            f"Não é possível alterar o status de {pedido.status} para {payload.status}"
        )

    pedido.status = payload.status

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc

    db.refresh(pedido)
    notificacoes_eventos.notificar_pedido_comprado(db, pedido)
    return pedido


def entregar_pedido(db: Session, pedido_id: int, background_tasks: BackgroundTasks | None = None) -> Pedido:
    pedido = get_pedido_by_id(db, pedido_id)

    if pedido.status != 2:
        raise PedidoCannotBeDeliveredError

    pedido.status = 3
    # A baixa já foi feita e auditada na aprovação (movimento pedido_aprovado).
    # Somar o estoque aqui duplicaria a movimentação e zeraria o consumo real.

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc

    db.refresh(pedido)
    notificacoes_eventos.notificar_pedido_entregue(db, pedido)
    return pedido


def delete_pedido(db: Session, pedido_id: int) -> None:
    pedido = get_pedido_by_id(db, pedido_id)
    db.delete(pedido)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PedidoHasDependenciesError from exc
