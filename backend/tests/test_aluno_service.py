import pytest
from sqlalchemy.orm import Session

from app.schemas.aluno_schema import AlunoCreateSchema, AlunoUpdateSchema
from app.services.aluno_service import (
    AlunoNotFoundError,
    create_aluno,
    get_aluno_by_id,
    list_alunos,
    update_aluno,
    delete_aluno,
)


class TestCreateAluno:
    def test_creates_successfully(self, db_session: Session):
        payload = AlunoCreateSchema(nome="Novo Aluno", telefone="11888888888")
        result = create_aluno(db_session, payload)
        assert result.nome == "Novo Aluno"
        assert result.id_aluno is not None


class TestListAlunos:
    def test_lists_all(self, db_session: Session, aluno):
        results = list_alunos(db_session)
        assert len(results) >= 1
        assert any(a.nome == "Aluno Teste" for a in results)


class TestGetAlunoById:
    def test_finds_existing(self, db_session: Session, aluno):
        result = get_aluno_by_id(db_session, aluno.id_aluno)
        assert result.nome == "Aluno Teste"

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(AlunoNotFoundError):
            get_aluno_by_id(db_session, 9999)


class TestUpdateAluno:
    def test_updates_fields(self, db_session: Session, aluno):
        payload = AlunoUpdateSchema(nome="Aluno Atualizado")
        result = update_aluno(db_session, aluno.id_aluno, payload)
        assert result.nome == "Aluno Atualizado"

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = AlunoUpdateSchema(nome="Qualquer")
        with pytest.raises(AlunoNotFoundError):
            update_aluno(db_session, 9999, payload)


class TestDeleteAluno:
    def test_deletes_existing(self, db_session: Session, aluno):
        delete_aluno(db_session, aluno.id_aluno)
        with pytest.raises(AlunoNotFoundError):
            get_aluno_by_id(db_session, aluno.id_aluno)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(AlunoNotFoundError):
            delete_aluno(db_session, 9999)
