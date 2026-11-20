from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.presenca import Presenca
from app.schemas.presenca_schema import PresencaBatchSchema, PresencaItemSchema
from app.services.presenca_service import (
    InvalidMatriculasError,
    create_or_update_presencas,
    list_presencas_by_turma,
)


class TestCreateOrUpdatePresencas:
    def test_creates_presencas(self, db_session: Session, turma, matricula_ativa):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=matricula_ativa.id_matricula, presente=True)],
        )
        results = create_or_update_presencas(db_session, payload)
        assert len(results) == 1
        assert results[0].presente is True

    def test_updates_existing_presenca(self, db_session: Session, turma, matricula_ativa):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=matricula_ativa.id_matricula, presente=True)],
        )
        create_or_update_presencas(db_session, payload)

        payload.presencas[0].presente = False
        results = create_or_update_presencas(db_session, payload)
        assert results[0].presente is False

    def test_raises_para_matricula_fora_da_turma(self, db_session: Session, turma):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=9999, presente=True)],
        )
        with pytest.raises(InvalidMatriculasError) as exc:
            create_or_update_presencas(db_session, payload)
        assert exc.value.ids_invalidos == [9999]

    def test_batch_misto_nao_grava_nada(self, db_session: Session, turma, matricula_ativa):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[
                PresencaItemSchema(idMatricula=matricula_ativa.id_matricula, presente=True),
                PresencaItemSchema(idMatricula=9999, presente=True),
            ],
        )
        with pytest.raises(InvalidMatriculasError):
            create_or_update_presencas(db_session, payload)
        assert db_session.query(Presenca).count() == 0

    def test_ids_invalidos_repetidos_nao_duplicam(self, db_session: Session, turma):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[
                PresencaItemSchema(idMatricula=9999, presente=True),
                PresencaItemSchema(idMatricula=9999, presente=False),
                PresencaItemSchema(idMatricula=8888, presente=True),
            ],
        )
        with pytest.raises(InvalidMatriculasError) as exc:
            create_or_update_presencas(db_session, payload)
        assert exc.value.ids_invalidos == [9999, 8888]


class TestListPresencasByTurma:
    def test_lists_presencas(self, db_session: Session, turma, matricula_ativa):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=matricula_ativa.id_matricula, presente=True)],
        )
        create_or_update_presencas(db_session, payload)

        results = list_presencas_by_turma(db_session, turma.id_turma)
        assert len(results) == 1

    def test_filters_by_date(self, db_session: Session, turma, matricula_ativa):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=matricula_ativa.id_matricula, presente=True)],
        )
        create_or_update_presencas(db_session, payload)

        results = list_presencas_by_turma(db_session, turma.id_turma, data_aula=date(2026, 1, 1))
        assert len(results) == 0
