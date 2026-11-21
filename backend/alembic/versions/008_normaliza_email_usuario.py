"""normaliza email do usuario e cria indice funcional unico

Revision ID: 008
Revises: 007
Create Date: 2026-11-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A comparacao de login/recuperacao usa lower(email). Normalizar os dados
    # evita que linhas legadas em caixa mista ou com espacos gerem ambiguidade.
    duplicados = op.get_bind().execute(
        sa.text(
            """
            SELECT lower(trim(email)), count(*)
            FROM usuario
            WHERE email IS NOT NULL
            GROUP BY lower(trim(email))
            HAVING count(*) > 1
            """
        )
    ).fetchall()
    if duplicados:
        detalhes = ", ".join(f"{email} ({total})" for email, total in duplicados)
        raise RuntimeError(
            "Nao e possivel normalizar usuario.email: existem e-mails duplicados "
            f"ignorando caixa e espacos ({detalhes}). Resolva manualmente antes de migrar."
        )

    op.execute("UPDATE usuario SET email = lower(trim(email)) WHERE email IS NOT NULL")

    # O unique da coluna e case-sensitive; o indice funcional impede novos
    # cadastros que difiram apenas por caixa e atende a consulta lower(email).
    op.create_index(
        "uq_usuario_email_lower",
        "usuario",
        [sa.text("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_usuario_email_lower", table_name="usuario")
    # A normalizacao dos dados nao e revertida: o valor original nao e preservado.
