"""Add primeiro_acesso flag to usuario

Revision ID: 005
Revises: 004_add_endereco_to_usuario
Create Date: 2026-09-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005"
down_revision: Union[str, None] = "004_add_endereco_to_usuario"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column("primeiroacesso", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # Usuários já existentes já possuem senha definida: não devem ser forçados a trocá-la.
    op.execute("UPDATE usuario SET primeiroacesso = false")


def downgrade() -> None:
    op.drop_column("usuario", "primeiroacesso")
