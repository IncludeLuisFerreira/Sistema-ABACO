import pytest
from sqlalchemy.orm import Session

from app.schemas.turma_schema import TurmaCreateSchema, TurmaUpdateSchema
from app.services.turma_service import (
    CursoNotFoundForTurmaError,
    ProfessorNotFoundForTurmaError,
    TurmaNotFoundError,
    create_turma,
    get_turma_by_id,
    list_turmas,
    list_turmas_by_professor,
    update_turma,
    delete_turma,
)


class TestCreateTurma:
    def test_creates_successfully(self, db_session: Session, curso, usuario_professor):
        payload = TurmaCreateSchema(idCurso=curso.id_curso, idProfessor=usuario_professor.id_usuario, capacidade=20)
        result = create_turma(db_session, payload)
        assert result.capacidade == 20
        assert result.id_turma is not None

    def test_raises_for_unknown_curso(self, db_session: Session):
        payload = TurmaCreateSchema(idCurso=9999, capacidade=20)
        with pytest.raises(CursoNotFoundForTurmaError):
            create_turma(db_session, payload)

    def test_raises_for_unknown_professor(self, db_session: Session, curso):
        payload = TurmaCreateSchema(idCurso=curso.id_curso, idProfessor=9999, capacidade=20)
        with pytest.raises(ProfessorNotFoundForTurmaError):
            create_turma(db_session, payload)


class TestListTurmas:
    def test_lists_all(self, db_session: Session, turma):
        results = list_turmas(db_session)
        assert len(results) >= 1


class TestListTurmasByProfessor:
    def test_filters_by_professor(self, db_session: Session, turma, usuario_professor):
        results = list_turmas_by_professor(db_session, usuario_professor.id_usuario)
        assert len(results) == 1
        assert results[0].id_turma == turma.id_turma

    def test_returns_empty_for_other_professor(self, db_session: Session):
        results = list_turmas_by_professor(db_session, 9999)
        assert len(results) == 0


class TestGetTurmaById:
    def test_finds_existing(self, db_session: Session, turma):
        result = get_turma_by_id(db_session, turma.id_turma)
        assert result.id_turma == turma.id_turma

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(TurmaNotFoundError):
            get_turma_by_id(db_session, 9999)


class TestUpdateTurma:
    def test_updates_capacity(self, db_session: Session, turma):
        payload = TurmaUpdateSchema(capacidade=50)
        result = update_turma(db_session, turma.id_turma, payload)
        assert result.capacidade == 50

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = TurmaUpdateSchema(capacidade=10)
        with pytest.raises(TurmaNotFoundError):
            update_turma(db_session, 9999, payload)


class TestDeleteTurma:
    def test_deletes_existing(self, db_session: Session, turma):
        delete_turma(db_session, turma.id_turma)
        with pytest.raises(TurmaNotFoundError):
            get_turma_by_id(db_session, turma.id_turma)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(TurmaNotFoundError):
            delete_turma(db_session, 9999)
