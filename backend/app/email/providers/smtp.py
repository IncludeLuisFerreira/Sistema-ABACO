import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from app.core.config import get_settings
from app.email.exceptions import EmailDeliveryError
from app.email.messages import build_email_message

logger = logging.getLogger(__name__)


def send(to_email: str, subject: str, body: str, html: str | None = None) -> None:
    settings = get_settings()
    html_content = html or build_email_message(subject, body).html

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((settings.email_sender_name, settings.smtp_from))
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        if settings.smtp_port == 465:
            with smtplib.SMTP_SSL(
                host=settings.smtp_host,
                port=settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
            ) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
    except Exception as error:
        logger.error("Falha no envio SMTP (%s)", type(error).__name__)
        raise EmailDeliveryError("Falha no envio de e-mail via SMTP") from error
