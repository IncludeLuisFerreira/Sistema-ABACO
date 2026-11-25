from datetime import date
from types import SimpleNamespace

from app.email.messages import (
    EmailMessage,
    build_email_message,
    build_first_access_message,
    build_pedido_aprovado_message,
    build_reset_message,
)


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


def test_build_pedido_aprovado_message_has_order_date_and_items():
    subject, body = build_pedido_aprovado_message(
        42, date(2026, 11, 9), [("Papel A4", 3), ("Caneta", 10)]
    )

    assert subject == "SGA ABACO - Pedido #42 aprovado"
    assert "Pedido: #42" in body
    assert "Data da aprovação: 09/11/2026" in body
    assert "Papel A4: 3" in body
    assert "Caneta: 10" in body


def test_build_pedido_aprovado_message_without_items():
    _subject, body = build_pedido_aprovado_message(7, date(2026, 11, 9), [])

    assert "Nenhum item informado" in body


def test_build_email_message_tem_texto_html_e_cta():
    mensagem = build_email_message(
        "SGA ABACO - Pedido #42",
        "Linha 1\nLinha 2",
        link="http://localhost:3000/academico/pedidos",
        cta_label="Ver pedido",
    )

    assert isinstance(mensagem, EmailMessage)
    assert mensagem.subject == "SGA ABACO - Pedido #42"
    assert mensagem.text == "Linha 1\nLinha 2"
    assert "<br>" in mensagem.html
    assert "Linha 1" in mensagem.html
    assert "http://localhost:3000/academico/pedidos" in mensagem.html
    assert "Ver pedido" in mensagem.html


def test_build_email_message_escapa_dados_dinamicos():
    mensagem = build_email_message(
        "Curso <script>alert(1)</script>",
        'Turma & Curso "Especial" com <b>justificativa</b>',
        link="/pedidos?status=<1>&origem=inbox",
        cta_label="Ver <curso>",
    )

    assert "<script>" not in mensagem.html
    assert "&lt;script&gt;" in mensagem.html
    assert "&lt;b&gt;justificativa&lt;/b&gt;" in mensagem.html
    assert "Turma &amp; Curso &quot;Especial&quot;" in mensagem.html
    assert "status=&lt;1&gt;&amp;origem=inbox" in mensagem.html
    assert "Ver &lt;curso&gt;" in mensagem.html
    assert "<b>justificativa</b>" not in mensagem.html


def test_build_email_message_escapa_nome_curso_justificativa_e_observacao():
    mensagem = build_email_message(
        "SGA ABACO - Alerta",
        'Aluno <img src=x> do curso "Informática & Redes"\n'
        'Justificativa: <script>alert(1)</script>\n'
        'Observação: <b>revisar</b>',
    )

    assert "<img src=x>" not in mensagem.html
    assert "<script>" not in mensagem.html
    assert "<b>revisar</b>" not in mensagem.html
    assert "&lt;img src=x&gt;" in mensagem.html
    assert "&quot;Informática &amp; Redes&quot;" in mensagem.html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in mensagem.html
    assert "&lt;b&gt;revisar&lt;/b&gt;" in mensagem.html
    assert "<img src=x>" in mensagem.text
    assert "<script>alert(1)</script>" in mensagem.text


def test_build_email_message_sem_link_nao_gera_cta():
    mensagem = build_email_message("Assunto", "Somente texto")

    assert "Ver no SGA ABACO" not in mensagem.html
    assert "Somente texto" in mensagem.html
