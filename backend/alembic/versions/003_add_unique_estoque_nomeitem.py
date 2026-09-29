"""add unique estoque nomeitem lower

Revision ID: 003
Revises: b5aaca51a7ff
Create Date: 2026-09-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "b5aaca51a7ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Indice funcional case-insensitive para alinhar com a checagem
    # func.lower(nome_item) do servico. Se ja existirem nomes duplicados
    # ignorando caixa, a criacao do indice falha alto (nao remove dados).
    op.create_index(
        "uq_estoque_nomeitem_lower",
        "estoque",
        [sa.text("lower(nomeitem)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_estoque_nomeitem_lower", table_name="estoque")
