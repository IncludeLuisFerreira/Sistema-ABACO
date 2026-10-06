import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings
from app.email.exceptions import EmailDeliveryError

logger = logging.getLogger(__name__)


def send(to_email: str, subject: str, body: str) -> None:
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
    except Exception as error:
        logger.error("Falha no envio SMTP (%s)", type(error).__name__)
        raise EmailDeliveryError("Falha no envio de e-mail via SMTP") from error
