from datetime import date
from html import escape
from typing import NamedTuple


class EmailMessage(NamedTuple):
    """Conteúdo completo de um e-mail: texto para fallback e HTML para CTA."""

    subject: str
    text: str
    html: str


def build_email_message(
    subject: str,
    text: str,
    link: str | None = None,
    cta_label: str = "Ver no SGA ABACO",
) -> EmailMessage:
    """Monta HTML a partir do texto, escapando todos os dados interpolados."""
    linhas = "<br>".join(escape(linha) for linha in text.splitlines())
    cta = ""
    if link:
        cta = (
            '<p style="margin: 24px 0 0; text-align: center;">'
            f'<a href="{escape(link, quote=True)}" '
            'style="background-color: #0b5c4d; border-radius: 6px; color: #ffffff; '
            'display: inline-block; padding: 12px 20px; text-decoration: none;">'
            f"{escape(cta_label)}</a></p>"
        )
    html = (
        '<!doctype html><html lang="pt-BR"><body '
        'style="background-color: #f6f4ef; color: #1f2933; '
        'font-family: Arial, sans-serif; margin: 0; padding: 24px;">'
        '<div style="margin: 0 auto; max-width: 600px;">'
        f"<h1 style=\"font-size: 20px;\">{escape(subject)}</h1>"
        f'<div style="line-height: 1.5;">{linhas}</div>'
        f"{cta}"
        "<p style=\"color: #6b7280; font-size: 12px; margin-top: 32px;\">"
        "Mensagem automática do SGA ABACO. Não responda este e-mail.</p>"
        "</div></body></html>"
    )
    return EmailMessage(subject=subject, text=text, html=html)


class ItemEstoqueBaixo(NamedTuple):
    """Cópia dos dados do item no momento da queda, usada após o agendamento do e-mail."""

    nome: str
    saldo: int
    minimo: int
    unidade: str | None


def build_reset_message(settings, reset_token: str) -> tuple[str, str, str, str]:
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"

    subject = "SGA ABACO - Recuperação de Senha"
    body = f"""\
Olá,

Você solicitou a recuperação de senha no sistema SGA ABACO.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link é válido por {settings.reset_token_expire_minutes} minutos.

Se você não solicitou esta recuperação, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body, reset_link, "Link de recuperação"


def build_pedido_aprovado_message(
    pedido_id: int,
    data_aprovacao: date,
    itens: list[tuple[str, int]],
) -> tuple[str, str]:
    subject = f"SGA ABACO - Pedido #{pedido_id} aprovado"
    itens_descricao = "\n".join(
        f"- {nome}: {quantidade}" for nome, quantidade in itens
    ) or "- Nenhum item informado"
    body = f"""\
Olá,

Seu pedido de materiais foi aprovado.

Pedido: #{pedido_id}
Data da aprovação: {data_aprovacao.strftime('%d/%m/%Y')}

Itens aprovados:
{itens_descricao}

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body


def build_estoque_baixo_message(itens: list[ItemEstoqueBaixo]) -> tuple[str, str]:
    quantidade = len(itens)
    rotulo = "item" if quantidade == 1 else "itens"
    subject = f"SGA ABACO - Estoque baixo: {quantidade} {rotulo}"

    linhas = [
        f"- {item.nome}: saldo {item.saldo}, mínimo {item.minimo}, unidade {item.unidade or 'não informada'}"
        for item in itens
    ]
    body = f"""\
Olá,

Os seguintes itens de estoque atingiram ou ficaram abaixo do mínimo:

{chr(10).join(linhas)}

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body


def build_first_access_message(settings, first_access_token: str) -> tuple[str, str, str, str]:
    first_access_link = f"{settings.frontend_url}/first-access?token={first_access_token}"

    subject = "SGA ABACO - Conta criada com sucesso"
    body = f"""\
Olá,

Seu acesso ao sistema SGA ABACO foi criado.

Por segurança, defina sua senha pessoal no primeiro acesso clicando no link abaixo:
{first_access_link}

Este link é válido por {settings.first_access_token_expire_minutes} minutos.

Caso não reconheça este cadastro, ignore este e-mail.

Atenciosamente,
Equipe SGA ABACO
"""
    return subject, body, first_access_link, "Link de primeiro acesso"

