import json
import logging
import urllib.error
import urllib.request

from app.core.config import get_settings
from app.email.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TIMEOUT_SECONDS = 15


def send(to_email: str, subject: str, body: str) -> None:
    settings = get_settings()

    payload = json.dumps(
        {
            "sender": {"name": settings.email_sender_name, "email": settings.smtp_from},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": body,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        BREVO_API_URL,
        data=payload,
        headers={
            "api-key": settings.brevo_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=BREVO_TIMEOUT_SECONDS) as response:
            status_code = getattr(response, "status", None) or response.getcode()
            if status_code >= 400:
                raise EmailDeliveryError(f"Brevo respondeu com status {status_code}")
    except urllib.error.HTTPError as error:
        try:
            detail = error.read().decode("utf-8", errors="ignore")
        except Exception:
            detail = ""
        logger.error(
            "Falha ao enviar email via Brevo para %s: %s %s",
            to_email,
            error.code,
            detail,
        )
        raise EmailDeliveryError(detail) from error
    except (urllib.error.URLError, OSError) as error:
        logger.error("Falha de conexão com o Brevo ao enviar para %s: %s", to_email, error)
        raise EmailDeliveryError(str(error)) from error
