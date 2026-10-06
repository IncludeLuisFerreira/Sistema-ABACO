import logging
from types import SimpleNamespace

from app.email import send_first_access_email, send_reset_email
from app.email import service
from app.email.providers import brevo, console, smtp


def _settings(**overrides):
    base = {
        "frontend_url": "http://localhost:3000",
        "reset_token_expire_minutes": 15,
        "first_access_token_expire_minutes": 1440,
        "brevo_api_key": "",
        "email_sender_name": "SGA ABACO",
        "smtp_user": "",
        "smtp_password": "",
        "smtp_host": "localhost",
        "smtp_port": 587,
        "smtp_from": "noreply@abaco.org.br",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_selects_brevo_when_key_present():
    provider = service._select_provider(_settings(brevo_api_key="key"))
    assert provider is brevo.send


def test_selects_smtp_when_no_brevo_key():
    provider = service._select_provider(_settings(smtp_user="user@abaco.org.br"))
    assert provider is smtp.send


def test_blank_brevo_key_falls_through_to_smtp():
    provider = service._select_provider(
        _settings(brevo_api_key="   ", smtp_user="user@abaco.org.br")
    )
    assert provider is smtp.send


def test_selects_console_when_nothing_configured():
    assert service._select_provider(_settings()) is console.send


def test_send_reset_email_uses_console_fallback(monkeypatch, caplog):
    monkeypatch.setattr(service, "get_settings", lambda: _settings())
    with caplog.at_level(logging.INFO):
        send_reset_email("user@abaco.org.br", "reset123456")
    assert "reset123456" not in caplog.text


def test_send_first_access_email_uses_console_fallback(monkeypatch, caplog):
    monkeypatch.setattr(service, "get_settings", lambda: _settings())
    with caplog.at_level(logging.INFO):
        send_first_access_email("novo@abaco.org.br", "first123456")
    assert "first123456" not in caplog.text
