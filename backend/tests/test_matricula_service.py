import pytest
from sqlalchemy.orm import Session

from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaUpdateSchema
from app.services.matricula_service import (
    AlunoNotFoundForMatriculaError,
    MatriculaDuplicadaError,
    MatriculaNotFoundError,
    create_matricula,
    get_matricula_by_id,
    list_matriculas,
    update_matricula,
    delete_matricula,
)


class TestCreateMatricula:
    def test_creates_successfully(self, db_session: Session, aluno, turma):
        payload = MatriculaCreateSchema(idAluno=aluno.id_aluno, idTurma=turma.id_turma, status=0)
        result = create_matricula(db_session, payload)
        assert result.id_matricula is not None

    def test_raises_for_unknown_aluno(self, db_session: Session, turma):
        payload = MatriculaCreateSchema(idAluno=9999, idTurma=turma.id_turma, status=0)
        with pytest.raises(AlunoNotFoundForMatriculaError):
            create_matricula(db_session, payload)

    def test_raises_for_duplicate(self, db_session: Session, aluno, turma):
        payload = MatriculaCreateSchema(idAluno=aluno.id_aluno, idTurma=turma.id_turma, status=0)
        create_matricula(db_session, payload)
        with pytest.raises(MatriculaDuplicadaError):
            create_matricula(db_session, payload)


class TestListMatriculas:
    def test_lists_all(self, db_session: Session, matricula_ativa):
        results = list_matriculas(db_session)
        assert len(results) >= 1


class TestGetMatriculaById:
    def test_finds_existing(self, db_session: Session, matricula_ativa):
        result = get_matricula_by_id(db_session, matricula_ativa.id_matricula)
        assert result.id_matricula == matricula_ativa.id_matricula

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(MatriculaNotFoundError):
            get_matricula_by_id(db_session, 9999)


class TestUpdateMatricula:
    def test_updates_status(self, db_session: Session, matricula_ativa):
        payload = MatriculaUpdateSchema(status=1)
        result = update_matricula(db_session, matricula_ativa.id_matricula, payload)
        assert result.status == 1

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = MatriculaUpdateSchema(status=1)
        with pytest.raises(MatriculaNotFoundError):
            update_matricula(db_session, 9999, payload)


class TestDeleteMatricula:
    def test_deletes_existing(self, db_session: Session, matricula_ativa):
        delete_matricula(db_session, matricula_ativa.id_matricula)
        with pytest.raises(MatriculaNotFoundError):
            get_matricula_by_id(db_session, matricula_ativa.id_matricula)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(MatriculaNotFoundError):
            delete_matricula(db_session, 9999)
