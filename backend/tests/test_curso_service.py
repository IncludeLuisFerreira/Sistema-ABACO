import pytest
from sqlalchemy.orm import Session

from app.schemas.curso_schema import CursoCreateSchema, CursoUpdateSchema
from app.services.curso_service import (
    CursoNotFoundError,
    create_curso,
    get_curso_by_id,
    list_cursos,
    update_curso,
    delete_curso,
)


class TestCreateCurso:
    def test_creates_successfully(self, db_session: Session):
        payload = CursoCreateSchema(nomeCurso="Curso de Python")
        result = create_curso(db_session, payload)
        assert result.nome_curso == "Curso de Python"
        assert result.id_curso is not None


class TestListCursos:
    def test_lists_all(self, db_session: Session, curso):
        results = list_cursos(db_session)
        assert len(results) >= 1
        assert any(c.nome_curso == "Curso Teste" for c in results)


class TestGetCursoById:
    def test_finds_existing(self, db_session: Session, curso):
        result = get_curso_by_id(db_session, curso.id_curso)
        assert result.nome_curso == "Curso Teste"

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(CursoNotFoundError):
            get_curso_by_id(db_session, 9999)


class TestUpdateCurso:
    def test_updates_name(self, db_session: Session, curso):
        payload = CursoUpdateSchema(nomeCurso="Curso Atualizado")
        result = update_curso(db_session, curso.id_curso, payload)
        assert result.nome_curso == "Curso Atualizado"

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = CursoUpdateSchema(nomeCurso="Qualquer")
        with pytest.raises(CursoNotFoundError):
            update_curso(db_session, 9999, payload)


class TestDeleteCurso:
    def test_deletes_existing(self, db_session: Session, curso):
        delete_curso(db_session, curso.id_curso)
        with pytest.raises(CursoNotFoundError):
            get_curso_by_id(db_session, curso.id_curso)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(CursoNotFoundError):
            delete_curso(db_session, 9999)
