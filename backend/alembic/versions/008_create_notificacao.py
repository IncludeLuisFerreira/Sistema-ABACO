"""Create notificacao

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
    op.create_table(
        "notificacao",
        sa.Column("idnotificacao", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "idusuario",
            sa.Integer(),
            sa.ForeignKey("usuario.idusuario", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("link", sa.Text(), nullable=True),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "criada_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("idx_notificacao_idusuario_lida", "notificacao", ["idusuario", "lida"])
    op.create_index("idx_notificacao_idusuario_criada_em", "notificacao", ["idusuario", "criada_em"])


def downgrade() -> None:
    op.drop_index("idx_notificacao_idusuario_criada_em", table_name="notificacao")
    op.drop_index("idx_notificacao_idusuario_lida", table_name="notificacao")
    op.drop_table("notificacao")
