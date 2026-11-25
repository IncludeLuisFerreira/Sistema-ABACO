import logging
from datetime import date

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.email.messages import (
    EmailMessage,
    ItemEstoqueBaixo,
    build_email_message,
    build_estoque_baixo_message,
    build_pedido_aprovado_message,
)
from app.models.estoque import Estoque
from app.models.pedido import Pedido
from app.models.usuario import Usuario
from app.services.notificacao_dispatcher_service import (
    DestinatarioNotificacao,
    EventoNotificacao,
    disparar_evento,
)

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


def _link_absoluto(link: str | None) -> str | None:
    if not link:
        return None
    base = (getattr(get_settings(), "frontend_url", "") or "").rstrip("/")
    return f"{base}{link}" if base else link


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
) -> list[DestinatarioNotificacao]:
    return [
        DestinatarioNotificacao(usuario.id_usuario, link)
        for usuario in _usuarios_por_cargo(db, cargos, excluir_id)
    ]


def notificar_pedido_criado(db: Session, pedido: Pedido, usuario_id: int) -> None:
    autor = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    nome = (autor.nome if autor else None) or f"Usuário #{usuario_id}"
    turma = pedido.turma
    turma_descricao = f"Turma #{pedido.id_turma}"
    if turma is not None and turma.curso is not None and turma.curso.nome_curso:
        turma_descricao += f" ({turma.curso.nome_curso})"

    # Os destinatários são diretores; o link precisa ser o da área administrativa,
    # independentemente do cargo de quem criou o pedido.
    evento = EventoNotificacao(
        tipo="pedido_criado",
        titulo="Novo pedido aguardando aprovação",
        mensagem=(
            f"Pedido #{pedido.id_pedido} de {nome} - "
            f"{turma_descricao} aguardando aprovação."
        ),
    )
    disparar_evento(
        db,
        evento,
        _destinatarios_por_cargo(db, (1,), LINK_PEDIDOS_ADMIN, excluir_id=usuario_id),
    )


def _email_pedido_aprovado(
    pedido_id: int, link: str, itens: list[tuple[str, int]]
) -> EmailMessage:
    subject, texto = build_pedido_aprovado_message(pedido_id, date.today(), itens)
    return build_email_message(
        subject, texto, link=_link_absoluto(link), cta_label="Ver pedido"
    )


def notificar_pedido_aprovado(
    db: Session,
    pedido: Pedido,
    background_tasks: BackgroundTasks | None = None,
) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning(
            "Pedido #%s aprovado sem solicitante válido; notificação in-app ignorada",
            pedido.id_pedido,
        )
        return

    link = link_pedidos_para_cargo(solicitante.cargo)
    email = (solicitante.email or "").strip()
    if not email:
        logger.warning(
            "Pedido #%s aprovado sem envio de e-mail: solicitante não possui e-mail cadastrado",
            pedido.id_pedido,
        )

    itens = [
        (item.nome_item or f"Item #{item.id_item_estoque}", item.quantidade)
        for item in pedido.itens
        if item.quantidade is not None
    ]

    # O solicitante vem primeiro: se também for administrador, o dispatcher
    # deduplica por usuario_id e mantém o link da área acadêmica/administrativa dele.
    destinatarios = [
        DestinatarioNotificacao(
            solicitante.id_usuario, link, email=email, enviar_email=bool(email)
        )
    ]
    destinatarios.extend(
        DestinatarioNotificacao(usuario.id_usuario, LINK_PEDIDOS_ADMIN)
        for usuario in _usuarios_por_cargo(db, (3,))
    )

    evento = EventoNotificacao(
        tipo="pedido_aprovado",
        titulo=f"Pedido #{pedido.id_pedido} aprovado",
        mensagem=f"Seu pedido #{pedido.id_pedido} foi aprovado.",
        email=_email_pedido_aprovado(pedido.id_pedido, link, itens) if email else None,
    )
    disparar_evento(db, evento, destinatarios, background_tasks)


def notificar_pedido_comprado(db: Session, pedido: Pedido) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning(
            "Pedido #%s comprado sem solicitante válido; notificação in-app ignorada",
            pedido.id_pedido,
        )
        return

    evento = EventoNotificacao(
        tipo="pedido_comprado",
        titulo=f"Pedido #{pedido.id_pedido} comprado",
        mensagem=f"Seu pedido #{pedido.id_pedido} foi comprado.",
    )
    disparar_evento(
        db,
        evento,
        [
            DestinatarioNotificacao(
                solicitante.id_usuario, link_pedidos_para_cargo(solicitante.cargo)
            )
        ],
    )


def notificar_pedido_entregue(db: Session, pedido: Pedido) -> None:
    solicitante = _solicitante(db, pedido)
    if solicitante is None:
        logger.warning(
            "Pedido #%s entregue sem solicitante válido; notificação in-app ignorada",
            pedido.id_pedido,
        )
        return

    evento = EventoNotificacao(
        tipo="pedido_entregue",
        titulo=f"Pedido #{pedido.id_pedido} entregue",
        mensagem=f"Seu pedido #{pedido.id_pedido} foi entregue.",
    )
    disparar_evento(
        db,
        evento,
        [
            DestinatarioNotificacao(
                solicitante.id_usuario, link_pedidos_para_cargo(solicitante.cargo)
            )
        ],
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


def _email_estoque_baixo(itens: list[ItemEstoqueBaixo]) -> EmailMessage:
    subject, texto = build_estoque_baixo_message(itens)
    return build_email_message(
        subject,
        texto,
        link=_link_absoluto(LINK_ESTOQUE_ADMIN),
        cta_label="Ver estoque",
    )


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
    destinatarios: list[DestinatarioNotificacao] = []
    com_email = False
    for usuario in usuarios:
        email = (usuario.email or "").strip()
        com_email = com_email or bool(email)
        destinatarios.append(
            DestinatarioNotificacao(
                usuario.id_usuario,
                LINK_ESTOQUE_ADMIN,
                email=email,
                enviar_email=bool(email),
            )
        )

    if not com_email:
        logger.warning("Nenhum destinatário com e-mail cadastrado para alerta de estoque baixo")

    evento = EventoNotificacao(
        tipo="estoque_baixo",
        titulo=f"{quantidade} {rotulo} com estoque abaixo do mínimo",
        mensagem=_montar_mensagem_estoque_baixo(itens),
        email=_email_estoque_baixo(itens) if com_email else None,
    )
    disparar_evento(db, evento, destinatarios, background_tasks)
