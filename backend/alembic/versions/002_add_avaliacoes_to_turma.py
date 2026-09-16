"""Add avaliacoes JSON field to turma

Revision ID: 002
Revises: 001
Create Date: 2026-06-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # REFACTOR: migration usa JSONB e o model usa JSON; autogenerate fica ruidoso
    op.add_column("turma", sa.Column("avaliacoes", postgresql.JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("turma", "avaliacoes")
