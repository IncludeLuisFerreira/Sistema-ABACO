import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, body: str, html: bool = False) -> None:
    """
    Função base para enviar e-mails. Lida com a conexão SMTP.
    """
    settings = get_settings()

    if not settings.smtp_user:
        logger.info("SMTP não configurado. Simulação de envio para %s | Assunto: %s", to_email, subject)
        logger.debug("Conteúdo da mensagem:\n%s", body)
        return

    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Permite enviar tanto texto puro quanto HTML
    mime_type = "html" if html else "plain"
    msg.attach(MIMEText(body, mime_type, "utf-8"))

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


def send_reset_email(to_email: str, reset_token: str) -> None:
    """
    Monta e envia o e-mail de recuperação de senha.
    """
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
    send_email(to_email=to_email, subject=subject, body=body)


def email_primeiro_acesso(destinatario: str, mensagem: str) -> None:
    """
    Envia as credenciais temporárias para o primeiro acesso do usuário.
    A mensagem é recebida já montada de onde a função foi chamada.
    """
    subject = "SGA ABACO - Credenciais de Primeiro Acesso"
    
    # Chama a função genérica de envio
    send_email(to_email=destinatario, subject=subject, body=mensagem)