import logging
import smtplib
from types import SimpleNamespace

import pytest

from app.services import email_service


def _settings(**overrides):
    base = {
        "frontend_url": "http://localhost:3000",
        "smtp_user": "",
        "smtp_password": "",
        "smtp_host": "localhost",
        "smtp_port": 587,
        "smtp_from": "noreply@abaco.org.br",
        "reset_token_expire_minutes": 15,
        "first_access_token_expire_minutes": 1440,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class TestSendFirstAccessEmail:
    def test_logs_link_when_smtp_not_configured(self, monkeypatch, caplog):
        monkeypatch.setattr(email_service, "get_settings", lambda: _settings())
        with caplog.at_level(logging.INFO):
            email_service.send_first_access_email("novo@abaco.org.br", "token123")
        assert "first-access?token=token123" in caplog.text

    def test_sends_via_smtp_when_configured(self, monkeypatch):
        sent = {}

        class FakeSMTP:
            def __init__(self, host, port):
                sent["host"] = host
                sent["port"] = port

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def ehlo(self):
                pass

            def starttls(self):
                pass

            def login(self, user, password):
                sent["login"] = (user, password)

            def send_message(self, msg):
                sent["message"] = msg

        monkeypatch.setattr(email_service, "get_settings", lambda: _settings(smtp_user="user@abaco.org.br", smtp_password="secret"))
        monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSMTP)

        email_service.send_first_access_email("novo@abaco.org.br", "token123")

        assert sent["host"] == "localhost"
        assert sent["login"] == ("user@abaco.org.br", "secret")
        payload = sent["message"].get_payload()[0].get_payload(decode=True).decode("utf-8")
        assert "first-access?token=token123" in payload

    def test_propagates_smtp_errors(self, monkeypatch):
        class FailingSMTP:
            def __init__(self, host, port):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def ehlo(self):
                pass

            def starttls(self):
                pass

            def login(self, user, password):
                pass

            def send_message(self, msg):
                raise smtplib.SMTPException("boom")

        monkeypatch.setattr(email_service, "get_settings", lambda: _settings(smtp_user="user@abaco.org.br", smtp_password="secret"))
        monkeypatch.setattr(email_service.smtplib, "SMTP", FailingSMTP)

        with pytest.raises(smtplib.SMTPException):
            email_service.send_first_access_email("novo@abaco.org.br", "token123")


class TestSendResetEmail:
    def test_logs_link_when_smtp_not_configured(self, monkeypatch, caplog):
        monkeypatch.setattr(email_service, "get_settings", lambda: _settings())
        with caplog.at_level(logging.INFO):
            email_service.send_reset_email("user@abaco.org.br", "reset123")
        assert "reset-password?token=reset123" in caplog.text
