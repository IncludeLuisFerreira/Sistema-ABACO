from collections.abc import Callable
from datetime import date

from app.core.config import get_settings
from app.email import messages
from app.email.messages import ItemEstoqueBaixo
from app.email.providers import brevo, console, smtp


def get_email_provider_name(settings) -> str:
    if settings.brevo_api_key.strip():
        return "brevo"
    if settings.smtp_user.strip():
        return "smtp"
    return "console"


def _select_provider(settings) -> Callable[[str, str, str], None]:
    provider = get_email_provider_name(settings)
    if provider == "brevo":
        return brevo.send
    if provider == "smtp":
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


def send_estoque_baixo_email(to_email: str, itens: list[ItemEstoqueBaixo]) -> None:
    settings = get_settings()
    subject, body = messages.build_estoque_baixo_message(itens)
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

