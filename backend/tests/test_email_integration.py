import os

import pytest

from app.core.config import get_settings
from app.email import send_reset_email

RECIPIENT_ENV = "EMAIL_INTEGRATION_TO"
DEFAULT_RECIPIENT = "luisfelipeazul77@gmail.com"


def _provider_configured() -> bool:
    settings = get_settings()
    brevo_key = getattr(settings, "brevo_api_key", "") or ""
    smtp_user = getattr(settings, "smtp_user", "") or ""
    return bool(brevo_key.strip() or smtp_user.strip())


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_EMAIL_INTEGRATION") != "1",
        reason="Defina RUN_EMAIL_INTEGRATION=1 para enviar um e-mail real",
    ),
    pytest.mark.skipif(
        not _provider_configured(),
        reason="Configure BREVO_API_KEY ou SMTP_USER/SMTP_PASSWORD para envio real",
    ),
]


def test_sends_real_reset_email() -> None:
    to_email = os.getenv(RECIPIENT_ENV, DEFAULT_RECIPIENT)
    assert send_reset_email(to_email, "integration-test-token") is None
