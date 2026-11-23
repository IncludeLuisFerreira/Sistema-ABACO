from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaUpdateSchema
from app.services.matricula_service import (
    AlunoNotFoundForMatriculaError,
    MatriculaDuplicadaError,
    MatriculaNotFoundError,
    TurmaLotadaError,
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

    def test_updates_data_matricula(self, db_session: Session, matricula_ativa):
        payload = MatriculaUpdateSchema(dataMatricula=date(2026, 3, 1))
        result = update_matricula(db_session, matricula_ativa.id_matricula, payload)
        assert result.data_matricula == date(2026, 3, 1)

    def test_raises_for_nonexistent(self, db_session: Session):
        payload = MatriculaUpdateSchema(status=1)
        with pytest.raises(MatriculaNotFoundError):
            update_matricula(db_session, 9999, payload)

    def test_update_status_em_turma_cheia_nao_levanta(self, db_session: Session, matricula_ativa, turma):
        turma.capacidade = 1
        db_session.commit()

        payload = MatriculaUpdateSchema(
            idAluno=matricula_ativa.id_aluno, idTurma=turma.id_turma, status=1
        )
        result = update_matricula(db_session, matricula_ativa.id_matricula, payload)

        assert result.status == 1
        assert result.id_aluno == matricula_ativa.id_aluno
        assert result.id_turma == turma.id_turma

    def test_move_para_turma_lotada_levanta(self, db_session: Session, matricula_ativa, usuario_professor):
        outro_curso = Curso(nome_curso="Outro Curso")
        db_session.add(outro_curso)
        db_session.commit()
        db_session.refresh(outro_curso)

        turma_lotada = Turma(
            capacidade=1,
            id_curso=outro_curso.id_curso,
            id_professor=usuario_professor.id_usuario,
            dias_aula="1",
        )
        db_session.add(turma_lotada)
        db_session.commit()
        db_session.refresh(turma_lotada)

        aluno2 = Aluno(nome="Aluno Dois")
        db_session.add(aluno2)
        db_session.commit()
        db_session.refresh(aluno2)
        db_session.add(Matricula(id_aluno=aluno2.id_aluno, id_turma=turma_lotada.id_turma, status=0))
        db_session.commit()

        payload = MatriculaUpdateSchema(idTurma=turma_lotada.id_turma)
        with pytest.raises(TurmaLotadaError):
            update_matricula(db_session, matricula_ativa.id_matricula, payload)

    def test_update_gerando_duplicidade_levanta(self, db_session: Session, matricula_ativa, turma, usuario_professor):
        turma2 = Turma(
            capacidade=30,
            id_curso=turma.id_curso,
            id_professor=usuario_professor.id_usuario,
            dias_aula="1",
        )
        db_session.add(turma2)
        db_session.commit()
        db_session.refresh(turma2)

        aluno2 = Aluno(nome="Aluno Dois")
        db_session.add(aluno2)
        db_session.commit()
        db_session.refresh(aluno2)
        db_session.add(Matricula(id_aluno=aluno2.id_aluno, id_turma=turma2.id_turma, status=0))
        db_session.commit()

        payload = MatriculaUpdateSchema(idAluno=aluno2.id_aluno)
        with pytest.raises(MatriculaDuplicadaError):
            update_matricula(db_session, matricula_ativa.id_matricula, payload)

        assert matricula_ativa.id_aluno != aluno2.id_aluno
        assert matricula_ativa.id_turma == turma.id_turma


class TestDeleteMatricula:
    def test_deletes_existing(self, db_session: Session, matricula_ativa):
        delete_matricula(db_session, matricula_ativa.id_matricula)
        with pytest.raises(MatriculaNotFoundError):
            get_matricula_by_id(db_session, matricula_ativa.id_matricula)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(MatriculaNotFoundError):
            delete_matricula(db_session, 9999)
