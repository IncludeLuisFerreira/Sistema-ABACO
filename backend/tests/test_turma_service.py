from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.schemas.turma_schema import TurmaCreateSchema, TurmaUpdateSchema
from app.services.turma_service import (
    CampoObrigatorioError,
    CapacidadeAbaixoDasVagasError,
    CursoNotFoundForTurmaError,
    DatasInvalidasError,
    ProfessorCargoInvalidoError,
    ProfessorNotFoundForTurmaError,
    TurmaNotFoundError,
    create_turma,
    get_turma_by_id,
    list_turmas,
    list_turmas_by_professor,
    update_turma,
    delete_turma,
)


def create_payload(curso, professor, **overrides) -> TurmaCreateSchema:
    data = {
        "idCurso": curso.id_curso,
        "idProfessor": professor.id_usuario,
        "capacidade": 20,
        "dataInicio": date(2026, 3, 1),
        "dataFim": date(2026, 6, 30),
        "diasAula": "1,3,5",
    }
    data.update(overrides)
    return TurmaCreateSchema(**data)


def usuario_com_cargo(db_session: Session, cargo: int) -> Usuario:
    usuario = Usuario(
        nome=f"Usuario Cargo {cargo}",
        email=f"cargo{cargo}@abaco.org.br",
        senha_hash="hash",
        cargo=cargo,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def matricula_ativa_para(db_session: Session, turma: Turma, nome: str) -> Matricula:
    aluno = Aluno(nome=nome)
    db_session.add(aluno)
    db_session.commit()
    db_session.refresh(aluno)

    matricula = Matricula(id_aluno=aluno.id_aluno, id_turma=turma.id_turma, status=0)
    db_session.add(matricula)
    db_session.commit()
    db_session.refresh(matricula)
    return matricula


class TestCreateTurma:
    def test_creates_successfully(self, db_session: Session, curso, usuario_professor):
        result = create_turma(db_session, create_payload(curso, usuario_professor))

        assert result.capacidade == 20
        assert result.data_inicio == date(2026, 3, 1)
        assert result.dias_aula == "1,3,5"
        assert result.id_turma is not None

    def test_raises_for_unknown_curso(self, db_session: Session, usuario_professor):
        payload = TurmaCreateSchema(
            idCurso=9999,
            idProfessor=usuario_professor.id_usuario,
            capacidade=20,
            dataInicio=date(2026, 3, 1),
            dataFim=date(2026, 6, 30),
            diasAula="1",
        )

        with pytest.raises(CursoNotFoundForTurmaError):
            create_turma(db_session, payload)

    def test_raises_for_unknown_professor(self, db_session: Session, curso):
        payload = create_payload(curso, usuario_professor_placeholder(9999))

        with pytest.raises(ProfessorNotFoundForTurmaError):
            create_turma(db_session, payload)

    def test_raises_for_professor_with_wrong_cargo(self, db_session: Session, curso):
        diretor = usuario_com_cargo(db_session, 1)
        payload = create_payload(curso, diretor)

        with pytest.raises(ProfessorCargoInvalidoError):
            create_turma(db_session, payload)

    def test_raises_when_data_fim_is_before_data_inicio(self, db_session: Session, curso, usuario_professor):
        payload = create_payload(
            curso,
            usuario_professor,
            dataInicio=date(2026, 6, 30),
            dataFim=date(2026, 3, 1),
        )

        with pytest.raises(DatasInvalidasError):
            create_turma(db_session, payload)

    def test_accepts_equal_dates(self, db_session: Session, curso, usuario_professor):
        payload = create_payload(
            curso,
            usuario_professor,
            dataInicio=date(2026, 3, 1),
            dataFim=date(2026, 3, 1),
        )

        result = create_turma(db_session, payload)

        assert result.data_inicio == result.data_fim


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

    @pytest.mark.parametrize(
        "field",
        ["idCurso", "idProfessor", "capacidade", "dataInicio", "dataFim", "diasAula"],
    )
    def test_raises_when_clearing_required_field(self, db_session: Session, turma, field):
        payload = TurmaUpdateSchema(**{field: None})

        with pytest.raises(CampoObrigatorioError):
            update_turma(db_session, turma.id_turma, payload)

    def test_allows_empty_partial_update(self, db_session: Session, turma):
        result = update_turma(db_session, turma.id_turma, TurmaUpdateSchema())

        assert result.id_turma == turma.id_turma

    def test_raises_when_capacity_is_below_occupied_slots(self, db_session: Session, turma):
        matricula_ativa_para(db_session, turma, "Aluno 1")
        matricula_ativa_para(db_session, turma, "Aluno 2")

        with pytest.raises(CapacidadeAbaixoDasVagasError):
            update_turma(db_session, turma.id_turma, TurmaUpdateSchema(capacidade=1))

    def test_allows_capacity_equal_to_occupied_slots(self, db_session: Session, turma):
        matricula_ativa_para(db_session, turma, "Aluno 1")
        matricula_ativa_para(db_session, turma, "Aluno 2")

        result = update_turma(db_session, turma.id_turma, TurmaUpdateSchema(capacidade=2))

        assert result.capacidade == 2

    def test_raises_when_partial_date_update_inverts_range(self, db_session: Session, turma):
        payload = TurmaUpdateSchema(dataInicio=date(2026, 7, 1))

        with pytest.raises(DatasInvalidasError):
            update_turma(db_session, turma.id_turma, payload)

    def test_updates_legacy_turma_with_null_dates(self, db_session: Session, curso, usuario_professor):
        turma = Turma(
            capacidade=10,
            id_curso=curso.id_curso,
            id_professor=usuario_professor.id_usuario,
            dias_aula="1",
        )
        db_session.add(turma)
        db_session.commit()
        db_session.refresh(turma)

        result = update_turma(db_session, turma.id_turma, TurmaUpdateSchema(capacidade=15))

        assert result.capacidade == 15

    def test_raises_when_changing_to_non_professor(self, db_session: Session, turma):
        diretor = usuario_com_cargo(db_session, 1)

        with pytest.raises(ProfessorCargoInvalidoError):
            update_turma(db_session, turma.id_turma, TurmaUpdateSchema(idProfessor=diretor.id_usuario))

    def test_keeps_avaliacoes_when_explicitly_null(self, db_session: Session, curso, usuario_professor):
        turma = create_turma(
            db_session,
            create_payload(
                curso,
                usuario_professor,
                avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}],
            ),
        )

        result = update_turma(db_session, turma.id_turma, TurmaUpdateSchema(avaliacoes=None))

        assert result.avaliacoes is not None
        assert result.avaliacoes[0]["nome"] == "Prova 1"

    def test_clears_avaliacoes_when_empty_list(self, db_session: Session, curso, usuario_professor):
        turma = create_turma(
            db_session,
            create_payload(
                curso,
                usuario_professor,
                avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}],
            ),
        )

        result = update_turma(db_session, turma.id_turma, TurmaUpdateSchema(avaliacoes=[]))

        assert result.avaliacoes == []


class TestDeleteTurma:
    def test_deletes_existing(self, db_session: Session, turma):
        delete_turma(db_session, turma.id_turma)
        with pytest.raises(TurmaNotFoundError):
            get_turma_by_id(db_session, turma.id_turma)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(TurmaNotFoundError):
            delete_turma(db_session, 9999)


def usuario_professor_placeholder(usuario_id: int) -> Usuario:
    return Usuario(id_usuario=usuario_id, nome="Inexistente", cargo=2)
