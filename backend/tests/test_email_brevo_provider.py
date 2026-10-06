import urllib.error
from types import SimpleNamespace

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


def test_posts_to_brevo_api(monkeypatch):
    captured = {}

    class FakeResponse:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["api-key"] = request.get_header("Api-key")
        return FakeResponse()

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.urllib.request, "urlopen", fake_urlopen)
    brevo.send("dest@abaco.org.br", "Assunto", "Corpo")
    assert captured["url"] == brevo.BREVO_API_URL
    assert captured["api-key"] == "brevo-key"


def test_http_error_raises_email_delivery_error(monkeypatch):
    def failing_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            brevo.BREVO_API_URL, 401, "Unauthorized", {}, None
        )

    monkeypatch.setattr(brevo, "get_settings", lambda: _settings())
    monkeypatch.setattr(brevo.urllib.request, "urlopen", failing_urlopen)
    with pytest.raises(EmailDeliveryError):
        brevo.send("dest@abaco.org.br", "Assunto", "Corpo")
