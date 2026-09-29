import logging
import smtplib

import pytest

import app.services.email_service as email_service


class _FakeSettings:
    def __init__(self, *, smtp_user="user@abaco.org.br", smtp_port=465):
        self.smtp_user = smtp_user
        self.smtp_password = "secret"
        self.smtp_port = smtp_port
        self.smtp_host = "smtp.abaco.org.br"
        self.smtp_from = "noreply@abaco.org.br"
        self.frontend_url = "http://localhost:3000"
        self.reset_token_expire_minutes = 15


class _FakeServer:
    def __init__(self, *_args, **_kwargs):
        self.sent_message = None
        self.logged_in = False

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False

    def ehlo(self):
        return None

    def starttls(self):
        return None

    def login(self, *_args):
        self.logged_in = True

    def send_message(self, message):
        self.sent_message = message


def test_sem_smtp_configurado_nao_envia(monkeypatch, caplog):
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(email_service, "get_settings", lambda: _FakeSettings(smtp_user=""))
    email_service.send_reset_email("dest@abaco.org.br", "tok")
    assert "SMTP não configurado" in caplog.text


def test_envio_via_smtp_ssl_porta_465(monkeypatch):
    server = _FakeServer()
    monkeypatch.setattr(email_service, "get_settings", lambda: _FakeSettings(smtp_port=465))
    monkeypatch.setattr(smtplib, "SMTP_SSL", lambda *_args, **_kwargs: server)

    email_service.send_reset_email("dest@abaco.org.br", "tok-123")

    assert server.logged_in is True
    assert server.sent_message is not None
    assert "Recuperação de Senha" in server.sent_message["Subject"]


def test_envio_via_smtp_tls_porta_587(monkeypatch):
    server = _FakeServer()
    monkeypatch.setattr(email_service, "get_settings", lambda: _FakeSettings(smtp_port=587))
    monkeypatch.setattr(smtplib, "SMTP", lambda *_args, **_kwargs: server)

    email_service.send_reset_email("dest@abaco.org.br", "tok-456")

    assert server.sent_message is not None


def test_falha_smtp_propaga_excecao(monkeypatch):
    class _FailingServer(_FakeServer):
        def __enter__(self):
            raise smtplib.SMTPException("falha simulada")

    monkeypatch.setattr(email_service, "get_settings", lambda: _FakeSettings(smtp_port=465))
    monkeypatch.setattr(smtplib, "SMTP_SSL", lambda *_args, **_kwargs: _FailingServer())

    with pytest.raises(smtplib.SMTPException):
        email_service.send_reset_email("dest@abaco.org.br", "tok-789")
