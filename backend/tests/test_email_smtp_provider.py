import smtplib
from types import SimpleNamespace

import pytest

from app.email.exceptions import EmailDeliveryError
from app.email.providers import smtp


def _settings(**overrides):
    base = {
        "smtp_host": "localhost",
        "smtp_port": 587,
        "smtp_user": "user@abaco.org.br",
        "smtp_password": "secret",
        "smtp_from": "noreply@abaco.org.br",
        "smtp_timeout_seconds": 15,
        "email_sender_name": "SGA ABACO",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_sends_via_starttls_on_587(monkeypatch):
    calls = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None):
            calls["host"] = host
            calls["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def ehlo(self):
            pass

        def starttls(self):
            calls["tls"] = True

        def login(self, user, password):
            calls["login"] = (user, password)

        def send_message(self, msg):
            calls["msg"] = msg

    monkeypatch.setattr(smtp, "get_settings", lambda: _settings())
    monkeypatch.setattr(smtp.smtplib, "SMTP", FakeSMTP)
    smtp.send("dest@abaco.org.br", "Assunto", "Corpo")
    assert calls["host"] == "localhost"
    assert calls["timeout"] == 15
    assert calls["tls"] is True
    assert calls["login"] == ("user@abaco.org.br", "secret")
    assert calls["msg"]["From"] == "SGA ABACO <noreply@abaco.org.br>"


def test_uses_smtp_ssl_on_465(monkeypatch):
    calls = {}

    class FakeSSL:
        def __init__(self, host, port, timeout=None):
            calls["ssl"] = True
            calls["timeout"] = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def login(self, user, password):
            pass

        def send_message(self, msg):
            pass

    monkeypatch.setattr(smtp, "get_settings", lambda: _settings(smtp_port=465))
    monkeypatch.setattr(smtp.smtplib, "SMTP_SSL", FakeSSL)
    smtp.send("dest@abaco.org.br", "Assunto", "Corpo")
    assert calls["ssl"] is True
    assert calls["timeout"] == 15


def test_raises_email_delivery_error_on_failure(monkeypatch):
    class FailingSMTP:
        def __init__(self, host, port, timeout=None):
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
            raise smtplib.SMTPException("private credential")

    monkeypatch.setattr(smtp, "get_settings", lambda: _settings())
    monkeypatch.setattr(smtp.smtplib, "SMTP", FailingSMTP)
    with pytest.raises(EmailDeliveryError):
        smtp.send("dest@abaco.org.br", "Assunto", "Corpo")


def test_blank_smtp_from_falls_back_to_default():
    from app.core.config import Settings

    settings = Settings(_env_file=None, SMTP_FROM="   ")

    assert settings.smtp_from == "noreply@abaco.org.br"
