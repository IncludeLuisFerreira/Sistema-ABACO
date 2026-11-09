from collections.abc import Callable
from datetime import date

from app.core.config import get_settings
from app.email import messages
from app.email.providers import brevo, console, smtp


def _select_provider(settings) -> Callable[[str, str, str], None]:
    if settings.brevo_api_key.strip():
        return brevo.send
    if settings.smtp_user.strip():
        return smtp.send
    return console.send


def _send_email(settings, to_email: str, subject: str, body: str) -> None:
    provider = _select_provider(settings)
    provider(to_email, subject, body)


def send_reset_email(to_email: str, reset_token: str) -> None:
    settings = get_settings()
    subject, body, _link, _link_label = messages.build_reset_message(settings, reset_token)
    _send_email(settings, to_email, subject, body)


def send_first_access_email(to_email: str, first_access_token: str) -> None:
    settings = get_settings()
    subject, body, _link, _link_label = messages.build_first_access_message(
        settings, first_access_token
    )
    _send_email(settings, to_email, subject, body)


def send_pedido_aprovado_email(
    to_email: str,
    pedido_id: int,
    data_aprovacao: date,
    itens: list[tuple[str, int]],
) -> None:
    settings = get_settings()
    subject, body = messages.build_pedido_aprovado_message(
        pedido_id, data_aprovacao, itens
    )
    _send_email(settings, to_email, subject, body)

