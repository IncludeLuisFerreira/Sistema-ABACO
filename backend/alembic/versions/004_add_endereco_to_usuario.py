"""add_endereco_to_usuario

Revision ID: 004_add_endereco_to_usuario
Revises: b5aaca51a7ff
Create Date: 2026-09-22 16:35:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004_add_endereco_to_usuario'
down_revision: Union[str, None] = 'b5aaca51a7ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuario', sa.Column('endereco', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('usuario', 'endereco')
