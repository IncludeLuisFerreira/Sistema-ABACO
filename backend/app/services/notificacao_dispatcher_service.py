import logging
from dataclasses import dataclass

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.email.exceptions import EmailDeliveryError
from app.email.messages import EmailMessage
from app.email.service import send_email
from app.services.notificacao_service import notificar_usuarios

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DestinatarioNotificacao:
    """Um destinatário do evento. O primeiro link por usuario_id prevalece."""

    usuario_id: int
    link: str | None = None
    email: str | None = None
    enviar_email: bool = False


@dataclass(frozen=True)
class EventoNotificacao:
    """Evento já formatado: inbox para todos e, opcionalmente, e-mail por destinatário."""

    tipo: str
    titulo: str
    mensagem: str
    email: EmailMessage | None = None


def _dedup(destinatarios: list[DestinatarioNotificacao]) -> list[DestinatarioNotificacao]:
    unicos: dict[int, DestinatarioNotificacao] = {}
    for destinatario in destinatarios:
        unicos.setdefault(destinatario.usuario_id, destinatario)
    return list(unicos.values())


def _enviar_email(
    to_email: str, mensagem: EmailMessage, tipo: str, titulo: str
) -> None:
    """Best-effort: nenhuma falha de provedor pode desfazer a operação de negócio."""
    try:
        send_email(to_email, mensagem)
    except EmailDeliveryError:
        logger.error(
            "Falha ao enviar e-mail de notificação '%s' (%s) para %s",
            tipo,
            titulo,
            to_email,
        )
    except Exception:
        logger.exception(
            "Erro inesperado ao enviar e-mail de notificação '%s' (%s) para %s",
            tipo,
            titulo,
            to_email,
        )


def disparar_evento(
    db: Session,
    evento: EventoNotificacao,
    destinatarios: list[DestinatarioNotificacao],
    background_tasks: BackgroundTasks | None = None,
) -> int:
    """Único caminho de disparo: grava inbox e agenda e-mails, absorvendo falhas.

    A deduplicação é por usuario_id e o primeiro link prevalece. O retorno é a
    quantidade de notificações gravadas no inbox; e-mails são opcionais por
    destinatário e nunca revertem a transação que originou o evento.
    """
    unicos = _dedup(destinatarios)
    if not unicos:
        return 0

    try:
        quantidade = notificar_usuarios(
            db,
            [(destinatario.usuario_id, destinatario.link) for destinatario in unicos],
            evento.tipo,
            evento.titulo,
            evento.mensagem,
        )
    except Exception:
        logger.exception("Falha ao gravar notificação '%s'", evento.titulo)
        quantidade = 0

    if evento.email is not None:
        for destinatario in unicos:
            if not destinatario.enviar_email:
                continue
            to_email = (destinatario.email or "").strip()
            if not to_email:
                logger.warning(
                    "Destinatário %s sem e-mail cadastrado; e-mail '%s' não enviado",
                    destinatario.usuario_id,
                    evento.tipo,
                )
                continue

            # EmailMessage é imutável: a tarefa em background pode rodar depois
            # de a sessão do banco ser fechada sem carregar campos lazy.
            if background_tasks is not None:
                background_tasks.add_task(
                    _enviar_email, to_email, evento.email, evento.tipo, evento.titulo
                )
            else:
                _enviar_email(to_email, evento.email, evento.tipo, evento.titulo)

    return quantidade
