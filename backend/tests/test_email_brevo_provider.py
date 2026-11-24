from types import SimpleNamespace

import httpx
import pytest

from app.email.exceptions import EmailDeliveryError
from app.email.providers import brevo


def _settings(**overrides):
    base = {
        "brevo_api_key": "brevo-key",
        "email_sender_name": "SGA ABACO",
        "smtp_from": "noreply@abaco.org.br",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _request(url: str) -> httpx.Request:
    return httpx.Request("POST", url, headers={"api-key": "brevo-key"})


def test_posts_to_brevo_api(monkeypatch):
    captured = {}

    def fake_post(url, *, json, headers, timeout):
        captured["url"] = url
        captured["api-key"] = headers["api-key"]
        captured["json"] = json
        captured["timeout"] = timeout
        return httpx.Response(201, request=_request(url))

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.httpx, "post", fake_post)
    brevo.send("dest@abaco.org.br", "Assunto", "Corpo")
    assert captured["url"] == brevo.BREVO_API_URL
    assert captured["api-key"] == "brevo-key"
    assert captured["timeout"] == brevo.BREVO_TIMEOUT_SECONDS
    assert captured["json"]["to"] == [{"email": "dest@abaco.org.br"}]


def test_http_error_raises_email_delivery_error(monkeypatch):
    def fake_post(url, *, json, headers, timeout):
        return httpx.Response(401, request=_request(url))

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.httpx, "post", fake_post)
    with pytest.raises(EmailDeliveryError):
        brevo.send("dest@abaco.org.br", "Assunto", "Corpo")


def test_http_error_detail_is_truncated(monkeypatch):
    long_body = "x" * 1000

    def fake_post(url, *, json, headers, timeout):
        return httpx.Response(500, text=long_body, request=_request(url))

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.httpx, "post", fake_post)
    with pytest.raises(EmailDeliveryError) as excinfo:
        brevo.send("dest@abaco.org.br", "Assunto", "Corpo")
    assert len(str(excinfo.value)) == brevo.MAX_DETAIL_LENGTH


def test_connection_error_raises_email_delivery_error(monkeypatch):
    def fake_post(url, *, json, headers, timeout):
        raise httpx.ConnectTimeout("tempo esgotado")

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.httpx, "post", fake_post)
    with pytest.raises(EmailDeliveryError):
        brevo.send("dest@abaco.org.br", "Assunto", "Corpo")
