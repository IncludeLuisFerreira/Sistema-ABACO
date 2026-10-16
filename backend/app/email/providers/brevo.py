import logging

import httpx

from app.core.config import get_settings
from app.email.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TIMEOUT_SECONDS = 15
MAX_DETAIL_LENGTH = 500


def send(to_email: str, subject: str, body: str) -> None:
    settings = get_settings()

    payload = {
        "sender": {"name": settings.email_sender_name, "email": settings.smtp_from},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }

    try:
        response = httpx.post(
            BREVO_API_URL,
            json=payload,
            headers={
                "api-key": settings.brevo_api_key,
                "Accept": "application/json",
            },
            timeout=BREVO_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = error.response.text[:MAX_DETAIL_LENGTH]
        logger.error(
            "Falha ao enviar email via Brevo para %s: %s %s",
            to_email,
            error.response.status_code,
            detail,
        )
        raise EmailDeliveryError(detail) from error
    except (httpx.HTTPError, OSError) as error:
        logger.error("Falha de conexão com o Brevo ao enviar para %s: %s", to_email, error)
        raise EmailDeliveryError(str(error)) from error
