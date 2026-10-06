from types import SimpleNamespace

from app.email.messages import build_first_access_message, build_reset_message


def _settings(**overrides):
    base = {
        "frontend_url": "http://localhost:3000",
        "reset_token_expire_minutes": 15,
        "first_access_token_expire_minutes": 1440,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_build_reset_message_has_link_and_subject():
    subject, body, link, label = build_reset_message(_settings(), "abc123")
    assert subject == "SGA ABACO - Recuperação de Senha"
    assert link == "http://localhost:3000/reset-password?token=abc123"
    assert link in body
    assert "15 minutos" in body
    assert label == "Link de recuperação"


def test_build_first_access_message_has_link_and_subject():
    subject, body, link, label = build_first_access_message(_settings(), "xyz789")
    assert subject == "SGA ABACO - Conta criada com sucesso"
    assert link == "http://localhost:3000/first-access?token=xyz789"
    assert link in body
    assert "1440 minutos" in body
    assert label == "Link de primeiro acesso"
