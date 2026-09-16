"""add_nomeitem_to_itempedido

Revision ID: b5aaca51a7ff
Revises: 002
Create Date: 2026-06-26 21:25:24.545628
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b5aaca51a7ff'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('itempedido', sa.Column('nomeitem', sa.Text))


def downgrade() -> None:
    op.drop_column('itempedido', 'nomeitem')
