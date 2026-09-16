"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aluno",
        sa.Column("idaluno", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.Text, nullable=False),
        sa.Column("telefone", sa.Text),
        sa.Column("nascimento", sa.Date),
        sa.Column("rua", sa.Text),
        sa.Column("bairro", sa.Text),
        sa.Column("numero", sa.Integer),
    )

    op.create_table(
        "curso",
        sa.Column("idcurso", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nomecurso", sa.Text, nullable=False),
    )

    op.create_table(
        "usuario",
        sa.Column("idusuario", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nome", sa.Text),
        sa.Column("telefone", sa.Text),
        sa.Column("email", sa.Text, unique=True),
        sa.Column("senhahash", sa.Text),
        sa.Column("cargo", sa.Integer),
    )

    op.create_table(
        "turma",
        sa.Column("idturma", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("capacidade", sa.Integer),
        sa.Column("datainicio", sa.Date),
        sa.Column("datafim", sa.Date),
        sa.Column("idcurso", sa.Integer, sa.ForeignKey("curso.idcurso")),
        sa.Column("idprofessor", sa.Integer, sa.ForeignKey("usuario.idusuario")),
        sa.Column("diasaula", sa.Text),
    )

    op.create_table(
        "matricula",
        sa.Column("idmatricula", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("idaluno", sa.Integer, sa.ForeignKey("aluno.idaluno")),
        sa.Column("idturma", sa.Integer, sa.ForeignKey("turma.idturma")),
        sa.Column("datamatricula", sa.Date),
        sa.Column("status", sa.Integer),
    )

    op.create_table(
        "presenca",
        sa.Column("idpresenca", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("idmatricula", sa.Integer, sa.ForeignKey("matricula.idmatricula")),
        sa.Column("dataaula", sa.Date),
        sa.Column("presente", sa.Boolean),
    )

    op.create_table(
        "nota",
        sa.Column("idnota", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nota", sa.Float),
        sa.Column("prova", sa.Integer),
        sa.Column("idmatricula", sa.Integer, sa.ForeignKey("matricula.idmatricula")),
    )
    op.create_index("idx_nota_id_matricula", "nota", ["idmatricula"])
    op.create_index("idx_nota_matricula_prova", "nota", ["idmatricula", "prova"])

    op.create_table(
        "estoque",
        sa.Column("iditemestoque", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nomeitem", sa.Text),
        sa.Column("quantidadedisponivel", sa.Integer),
        sa.Column("unidade", sa.Text),
        sa.Column("estoqueminimo", sa.Integer),
    )

    op.create_table(
        "movimentacao_estoque",
        sa.Column("idmovimentacao", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("iditemestoque", sa.Integer, sa.ForeignKey("estoque.iditemestoque")),
        sa.Column("quantidade", sa.Integer, nullable=False),
        sa.Column("tipomovimentacao", sa.Text, nullable=False),
        sa.Column("justificativa", sa.Text),
        sa.Column("datamovimentacao", sa.DateTime, nullable=False),
    )

    op.create_table(
        "pedido",
        sa.Column("idpedido", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("idusuario", sa.Integer, sa.ForeignKey("usuario.idusuario")),
        sa.Column("idturma", sa.Integer, sa.ForeignKey("turma.idturma")),
        sa.Column("datapedido", sa.Date),
        sa.Column("status", sa.Integer),
    )

    op.create_table(
        "itempedido",
        sa.Column("iditempedido", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("idpedido", sa.Integer, sa.ForeignKey("pedido.idpedido")),
        sa.Column("iditemestoque", sa.Integer, sa.ForeignKey("estoque.iditemestoque")),
        sa.Column("quantidade", sa.Integer),
        sa.Column("precounitario", sa.Float),
    )


def downgrade() -> None:
    op.drop_table("itempedido")
    op.drop_table("pedido")
    op.drop_table("movimentacao_estoque")
    op.drop_table("estoque")
    op.execute("DROP INDEX IF EXISTS idx_nota_matricula_prova")
    op.execute("DROP INDEX IF EXISTS idx_nota_id_matricula")
    op.drop_table("nota")
    op.drop_table("presenca")
    op.drop_table("matricula")
    op.drop_table("turma")
    op.drop_table("usuario")
    op.drop_table("curso")
    op.drop_table("aluno")
