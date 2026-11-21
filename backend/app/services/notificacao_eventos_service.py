import logging

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.email import EmailDeliveryError, send_estoque_baixo_email
from app.email.messages import ItemEstoqueBaixo
from app.models.estoque import Estoque
from app.models.pedido import Pedido
from app.models.usuario import Usuario
from app.services.notificacao_service import notificar_usuarios

logger = logging.getLogger(__name__)

LINK_PEDIDOS_ACADEMICO = "/academico/pedidos"
LINK_PEDIDOS_ADMIN = "/admin/logistico/pedidos"
LINK_ESTOQUE_ADMIN = "/admin/logistico/estoque"

MENSAGEM_MAX_LENGTH = 500
ITENS_MENSAGEM_LIMIT = 5


def link_pedidos_para_cargo(cargo: int | None) -> str:
    """Professor usa a área acadêmica; diretor e administrador, a área administrativa."""
    if cargo == 2:
        return LINK_PEDIDOS_ACADEMICO
    return LINK_PEDIDOS_ADMIN


def _solicitante(db: Session, pedido: Pedido) -> Usuario | None:
    if pedido.usuario is not None:
        return pedido.usuario
    return db.query(Usuario).filter(Usuario.id_usuario == pedido.id_usuario).first()


def _usuarios_por_cargo(
    db: Session,
    cargos: tuple[int, ...],
    excluir_id: int | None = None,
) -> list[Usuario]:
    query = db.query(Usuario).filter(Usuario.cargo.in_(cargos))
    if excluir_id is not None:
        query = query.filter(Usuario.id_usuario != excluir_id)
    return query.order_by(Usuario.id_usuario).all()


def _destinatarios_por_cargo(
    db: Session,
    cargos: tuple[int, ...],
    link: str,
    excluir_id: int | None = None,
) -> list[tuple[int, str | None]]:
    return [
        (usuario.id_usuario, link)
        for usuario in _usuarios_por_cargo(db, cargos, excluir_id)
    ]


def _notificar(
    db: Session,
    destinatarios: list[tuple[int, str | None]],
    tipo: str,
    titulo: str,
    mensagem: str,
) -> int:
    """Nunca deixa a gravação do inbox interferir na operação de negócio."""
    try:
        return notificar_usuarios(db, destinatarios, tipo, titulo, mensagem)
    except Exception:
        logger.exception("Falha ao gravar notificação '%s'", titulo)
        return 0


def notificar_pedido_criado(db: Session, pedido: Pedido, usuario_id: int) -> None:
    autor = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    link = link_pedidos_para_cargo(autor.cargo if autor else None)
    nome = (autor.nome if autor else None) or f"Usuário #{usuario_id}"
    turma = pedido.turma
    turma_descricao = f"Turma #{pedido.id_turma}"
    if turma is not None and turma.curso is not None and turma.curso.nome_curso:
        turma_descricao += f" ({turma.curso.nome_curso})"

    _notificar(
        db,
        _destinatarios_por_cargo(db, (1,), link, excluir_id=usuario_id),
        "pedido_criado",
        "Novo pedido aguardando aprovação",
        f"Pedido #{pedido.id_pedido} de {nome} - {turma_descricao} aguardando aprovação.",
    )


def notificar_pedido_aprovado(db: Session, pedido: Pedido) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning("Pedido #%s aprovado sem solicitante válido; notificação in-app ignorada", pedido.id_pedido)
        return

    destinatarios: list[tuple[int, str | None]] = [
        (solicitante.id_usuario, link_pedidos_para_cargo(solicitante.cargo))
    ]
    # notificar_usuarios deduplica por id e mantém o primeiro link: se o solicitante
    # também for administrador, recebe apenas a notificação com o link admin.
    destinatarios.extend(_destinatarios_por_cargo(db, (3,), LINK_PEDIDOS_ADMIN))

    _notificar(
        db,
        destinatarios,
        "pedido_aprovado",
        f"Pedido #{pedido.id_pedido} aprovado",
        f"Seu pedido #{pedido.id_pedido} foi aprovado.",
    )


def notificar_pedido_comprado(db: Session, pedido: Pedido) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning("Pedido #%s comprado sem solicitante válido; notificação in-app ignorada", pedido.id_pedido)
        return

    _notificar(
        db,
        [(solicitante.id_usuario, link_pedidos_para_cargo(solicitante.cargo))],
        "pedido_comprado",
        f"Pedido #{pedido.id_pedido} comprado",
        f"Seu pedido #{pedido.id_pedido} foi comprado.",
    )


def notificar_pedido_entregue(db: Session, pedido: Pedido) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning("Pedido #%s entregue sem solicitante válido; notificação in-app ignorada", pedido.id_pedido)
        return

    _notificar(
        db,
        [(solicitante.id_usuario, link_pedidos_para_cargo(solicitante.cargo))],
        "pedido_entregue",
        f"Pedido #{pedido.id_pedido} entregue",
        f"Seu pedido #{pedido.id_pedido} foi entregue.",
    )


def snapshot_estoque(item: Estoque) -> ItemEstoqueBaixo | None:
    """Cópia imutável do estado de baixo estoque; None quando não há mínimo."""
    minimo = item.estoque_minimo
    if minimo is None:
        return None
    return ItemEstoqueBaixo(
        nome=item.nome_item or f"Item #{item.id_item_estoque}",
        saldo=item.quantidade_disponivel or 0,
        minimo=minimo,
        unidade=item.unidade,
    )


def itens_recem_baixos(
    anteriores: dict[int, ItemEstoqueBaixo | None],
    atuais: list[Estoque],
) -> list[ItemEstoqueBaixo]:
    """Itens que cruzaram o mínimo nesta operação, sem coluna de deduplicação.

    Um item sem mínimo nunca alerta. A transição é anterior acima do mínimo e
    novo saldo no/abaixo do mínimo; na criação não há estado anterior, então
    um item criado já baixo entra na lista.
    """
    cruzados: list[ItemEstoqueBaixo] = []
    for item in atuais:
        atual = snapshot_estoque(item)
        if atual is None:
            continue
        anterior = anteriores.get(item.id_item_estoque)
        if anterior is None:
            # Criação ou item que não tinha mínimo: só alerta se já nasceu baixo.
            if atual.saldo <= atual.minimo:
                cruzados.append(atual)
        elif anterior.saldo > anterior.minimo and atual.saldo <= atual.minimo:
            cruzados.append(atual)
    return cruzados


def _montar_mensagem_estoque_baixo(itens: list[ItemEstoqueBaixo]) -> str:
    visiveis = itens[:ITENS_MENSAGEM_LIMIT]
    descricoes = [
        f"{item.nome}: saldo {item.saldo}/{item.minimo} {item.unidade or ''}".strip()
        for item in visiveis
    ]
    mensagem = "Itens abaixo do mínimo: " + ", ".join(descricoes)
    excedentes = len(itens) - len(visiveis)
    if excedentes > 0:
        mensagem += f" e {excedentes} outros itens"
    return mensagem[:MENSAGEM_MAX_LENGTH]


def _enviar_email_estoque_baixo(email: str, itens: list[ItemEstoqueBaixo]) -> None:
    try:
        send_estoque_baixo_email(email, itens)
    except EmailDeliveryError:
        logger.error("Falha ao enviar e-mail de estoque baixo para %s", email)
    except Exception:
        logger.exception("Erro inesperado ao enviar e-mail de estoque baixo para %s", email)


def notificar_estoque_baixo(
    db: Session,
    itens: list[ItemEstoqueBaixo],
    background_tasks: BackgroundTasks | None = None,
) -> None:
    """Consolida alerta in-app e e-mail por operação de estoque, sem reverter a baixa."""
    if not itens:
        return

    quantidade = len(itens)
    rotulo = "item" if quantidade == 1 else "itens"
    usuarios = _usuarios_por_cargo(db, (1, 3))
    _notificar(
        db,
        [(usuario.id_usuario, LINK_ESTOQUE_ADMIN) for usuario in usuarios],
        "estoque_baixo",
        f"{quantidade} {rotulo} com estoque abaixo do mínimo",
        _montar_mensagem_estoque_baixo(itens),
    )

    emails = [(usuario, (usuario.email or "").strip()) for usuario in usuarios]
    destinatarios = [email for _usuario, email in emails if email]
    if not destinatarios:
        logger.warning("Nenhum destinatário com e-mail cadastrado para alerta de estoque baixo")
        return

    for email in destinatarios:
        copia = list(itens)
        if background_tasks is not None:
            background_tasks.add_task(_enviar_email_estoque_baixo, email, copia)
        else:
            _enviar_email_estoque_baixo(email, copia)
