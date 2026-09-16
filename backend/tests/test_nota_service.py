import pytest
from sqlalchemy.orm import Session

from app.schemas.nota_schema import NotaBatchSchema, NotaItemSchema
from app.services.nota_service import (
    InvalidMatriculasError,
    create_or_update_notas,
    list_notas_by_matricula,
    list_notas_by_turma,
    calcular_media_por_prova,
)


class TestCreateOrUpdateNotas:
    def test_creates_notas(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.5)],
        )
        results = create_or_update_notas(db_session, payload)
        assert len(results) == 1
        assert results[0].nota == 8.5

    def test_updates_existing_nota(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.5)],
        )
        create_or_update_notas(db_session, payload)

        payload.notas[0].nota = 9.0
        results = create_or_update_notas(db_session, payload)
        assert results[0].nota == 9.0

    def test_raises_for_invalid_matricula(self, db_session: Session, turma):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=9999, nota=8.5)],
        )
        with pytest.raises(InvalidMatriculasError):
            create_or_update_notas(db_session, payload)


class TestListNotasByMatricula:
    def test_lists_notas(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.5)],
        )
        create_or_update_notas(db_session, payload)

        results = list_notas_by_matricula(db_session, matricula_ativa.id_matricula)
        assert len(results) == 1
        assert results[0].nota == 8.5


class TestListNotasByTurma:
    def test_lists_by_turma(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.5)],
        )
        create_or_update_notas(db_session, payload)

        results = list_notas_by_turma(db_session, turma.id_turma)
        assert len(results) == 1

    def test_filters_by_prova(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.5)],
        )
        create_or_update_notas(db_session, payload)

        results = list_notas_by_turma(db_session, turma.id_turma, prova=2)
        assert len(results) == 0


class TestCalcularMediaPorProva:
    def test_calculates_average(self, db_session: Session, turma, matricula_ativa):
        payload = NotaBatchSchema(
            idTurma=turma.id_turma,
            prova=1,
            notas=[NotaItemSchema(idMatricula=matricula_ativa.id_matricula, nota=8.0)],
        )
        create_or_update_notas(db_session, payload)

        medias = calcular_media_por_prova(db_session, turma.id_turma)
        assert len(medias) == 1
        assert medias[0].prova == 1
        assert medias[0].media == 8.0
