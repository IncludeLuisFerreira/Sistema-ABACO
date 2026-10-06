from collections.abc import Callable

from app.core.config import get_settings
from app.email import messages
from app.email.providers import brevo, console, smtp


def _select_provider(settings) -> Callable[[str, str, str], None]:
    if getattr(settings, "brevo_api_key", "").strip():
        return brevo.send
    if getattr(settings, "smtp_user", "").strip():
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
