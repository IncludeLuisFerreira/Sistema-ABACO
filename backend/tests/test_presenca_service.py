from datetime import date

from sqlalchemy.orm import Session

from app.schemas.presenca_schema import PresencaBatchSchema, PresencaItemSchema
from app.services.presenca_service import create_or_update_presencas, list_presencas_by_turma


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

    def test_ignores_matriculas_not_in_turma(self, db_session: Session, turma):
        payload = PresencaBatchSchema(
            idTurma=turma.id_turma,
            dataAula=date(2026, 6, 21),
            presencas=[PresencaItemSchema(idMatricula=9999, presente=True)],
        )
        results = create_or_update_presencas(db_session, payload)
        assert len(results) == 0


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
