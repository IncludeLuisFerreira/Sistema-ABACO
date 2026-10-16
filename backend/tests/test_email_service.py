import json
import logging
import smtplib
import urllib.error
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
        "email_sender_name": "SGA ABACO",
        "brevo_api_key": "",
        "reset_token_expire_minutes": 15,
        "first_access_token_expire_minutes": 1440,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class _FakeResponse:
    def __init__(self, status=201):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return self.status


class TestSendFirstAccessEmail:
    def test_logs_link_when_no_provider_configured(self, monkeypatch, caplog):
        monkeypatch.setattr(email_service, "get_settings", lambda: _settings())
        with caplog.at_level(logging.INFO):
            email_service.send_first_access_email("novo@abaco.org.br", "token123")
        assert "first-access?token=token123" in caplog.text

    def test_sends_via_brevo_when_api_key_configured(self, monkeypatch):
        captured = {}

        def fake_urlopen(request, timeout=None):
            captured["request"] = request
            captured["timeout"] = timeout
            return _FakeResponse(status=201)

        monkeypatch.setattr(
            email_service,
            "get_settings",
            lambda: _settings(brevo_api_key="brevo-key", smtp_user="ignorado@abaco.org.br"),
        )
        monkeypatch.setattr(email_service.urllib.request, "urlopen", fake_urlopen)

        email_service.send_first_access_email("qualquer-destinatario@gmail.com", "token123")

        request = captured["request"]
        assert request.full_url == email_service.BREVO_API_URL
        assert request.get_header("Api-key") == "brevo-key"
        payload = json.loads(request.data.decode("utf-8"))
        assert payload["to"] == [{"email": "qualquer-destinatario@gmail.com"}]
        assert payload["sender"] == {"name": "SGA ABACO", "email": "noreply@abaco.org.br"}
        assert payload["subject"] == "SGA ABACO - Conta criada com sucesso"
        assert "first-access?token=token123" in payload["textContent"]

    def test_propagates_brevo_http_errors(self, monkeypatch):
        def failing_urlopen(request, timeout=None):
            raise urllib.error.HTTPError(
                email_service.BREVO_API_URL,
                400,
                "Bad Request",
                hdrs=None,
                fp=__import__("io").BytesIO(b'{"message":"invalid"}'),
            )

        monkeypatch.setattr(email_service, "get_settings", lambda: _settings(brevo_api_key="brevo-key"))
        monkeypatch.setattr(email_service.urllib.request, "urlopen", failing_urlopen)

        with pytest.raises(email_service.EmailDeliveryError):
            email_service.send_first_access_email("novo@abaco.org.br", "token123")

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
    def test_logs_link_when_no_provider_configured(self, monkeypatch, caplog):
        monkeypatch.setattr(email_service, "get_settings", lambda: _settings())
        with caplog.at_level(logging.INFO):
            email_service.send_reset_email("user@abaco.org.br", "reset123")
        assert "reset-password?token=reset123" in caplog.text

    def test_sends_via_brevo_when_api_key_configured(self, monkeypatch):
        captured = {}

        def fake_urlopen(request, timeout=None):
            captured["request"] = request
            return _FakeResponse(status=201)

        monkeypatch.setattr(email_service, "get_settings", lambda: _settings(brevo_api_key="brevo-key"))
        monkeypatch.setattr(email_service.urllib.request, "urlopen", fake_urlopen)

        email_service.send_reset_email("user@abaco.org.br", "reset123")

        payload = json.loads(captured["request"].data.decode("utf-8"))
        assert payload["to"] == [{"email": "user@abaco.org.br"}]
        assert "reset-password?token=reset123" in payload["textContent"]
