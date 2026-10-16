import json
import logging
import smtplib
import urllib.error
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TIMEOUT_SECONDS = 15


class EmailDeliveryError(Exception):
    """Erro ao entregar e-mail por um provedor externo."""


def _send_via_brevo(to_email: str, subject: str, body: str) -> None:
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
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        logger.error("Falha ao enviar email via Brevo para %s: %s %s", to_email, e.code, detail)
        raise EmailDeliveryError(detail) from e
    except (urllib.error.URLError, OSError) as e:
        logger.error("Falha de conexão com o Brevo ao enviar para %s: %s", to_email, e)
        raise EmailDeliveryError(str(e)) from e


def _send_via_smtp(to_email: str, subject: str, body: str) -> None:
    settings = get_settings()

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(host=settings.smtp_host, port=settings.smtp_port) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
    except smtplib.SMTPException as e:
        logger.error("Falha ao enviar email para %s: %s", to_email, e)
        raise


def _deliver_email(to_email: str, subject: str, body: str, console_link: str, link_label: str) -> None:
    settings = get_settings()

    if getattr(settings, "brevo_api_key", ""):
        _send_via_brevo(to_email, subject, body)
        return

    if settings.smtp_user:
        _send_via_smtp(to_email, subject, body)
        return

    # FIXME: loga o link em texto puro, vazando o token quando não há provedor configurado
    logger.info("Nenhum provedor de e-mail configurado. %s para %s: %s", link_label, to_email, console_link)


def send_reset_email(to_email: str, reset_token: str) -> None:
    settings = get_settings()

    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"

    subject = "SGA ABACO - Recuperação de Senha"
    body = f"""\
Olá,

Você solicitou a recuperação de senha no sistema SGA ABACO.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link é válido por {settings.reset_token_expire_minutes} minutos.

Se você não solicitou esta recuperação, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    _deliver_email(to_email, subject, body, reset_link, "Link de recuperação")


def send_first_access_email(to_email: str, first_access_token: str) -> None:
    settings = get_settings()

    first_access_link = f"{settings.frontend_url}/first-access?token={first_access_token}"

    subject = "SGA ABACO - Conta criada com sucesso"
    body = f"""\
Olá,

Sua conta no sistema SGA ABACO foi criada com sucesso.

Por segurança, defina sua senha pessoal no primeiro acesso clicando no link abaixo:
{first_access_link}

Este link é válido por {settings.first_access_token_expire_minutes} minutos.

Caso não reconheça este cadastro, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    _deliver_email(to_email, subject, body, first_access_link, "Link de primeiro acesso")
