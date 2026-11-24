import pytest
from sqlalchemy.exc import IntegrityError

from app.db.errors import is_unique_violation


class _ErroOriginal:
    """Simula o erro do driver (psycopg no PostgreSQL, sqlite3 nos testes)."""

    def __init__(self, mensagem: str, pgcode: str | None = None):
        self._mensagem = mensagem
        self.pgcode = pgcode

    def __str__(self) -> str:
        return self._mensagem


def _integrity_error(mensagem: str, pgcode: str | None = None) -> IntegrityError:
    return IntegrityError("INSERT INTO tabela", {}, _ErroOriginal(mensagem, pgcode))


def test_pgcode_23505_e_violacao_unica():
    assert is_unique_violation(_integrity_error("erro generico", pgcode="23505"))


def test_mensagem_do_sqlite_e_violacao_unica():
    assert is_unique_violation(_integrity_error("UNIQUE constraint failed: estoque.nomeitem"))


def test_nome_do_indice_e_violacao_unica():
    assert is_unique_violation(_integrity_error("violates unique constraint uq_estoque_nomeitem_lower"))


def test_outro_erro_de_integridade_nao_e_unico():
    assert not is_unique_violation(_integrity_error("NOT NULL constraint failed: aluno.nome"))


def test_pgcode_de_foreign_key_nao_e_unico():
    assert not is_unique_violation(_integrity_error("foreign key violation", pgcode="23503"))
