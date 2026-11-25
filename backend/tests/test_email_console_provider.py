import logging

from app.email.providers import console


def test_logs_masked_token(caplog):
    body = "Acesse http://localhost:3000/reset-password?token=segredo123456789"
    with caplog.at_level(logging.INFO):
        console.send("user@abaco.org.br", "Assunto", body)
    assert "segredo123456789" not in caplog.text
    assert "segredo1" in caplog.text
    assert "user@abaco.org.br" in caplog.text


def test_short_token_is_fully_masked(caplog):
    body = "Acesse http://localhost:3000/reset-password?token=abc123"
    with caplog.at_level(logging.INFO):
        console.send("user@abaco.org.br", "Assunto", body)
    assert "abc123" not in caplog.text
    assert "token=..." in caplog.text


def test_body_without_token_does_not_crash(caplog):
    with caplog.at_level(logging.INFO):
        console.send("user@abaco.org.br", "Assunto", "Sem link aqui")
    assert "Sem link aqui" not in caplog.text


def test_console_loga_apenas_texto_nunca_html(caplog):
    html = "<p>Conteúdo exclusivo do HTML</p>"
    body = "Texto para console: token=abcdef123456789"
    with caplog.at_level(logging.INFO):
        console.send("user@abaco.org.br", "Assunto", body, html)
    assert "Texto para console" in caplog.text
    assert "abcdef123456789" not in caplog.text
    assert "Conteúdo exclusivo do HTML" not in caplog.text
    assert "<p>" not in caplog.text
