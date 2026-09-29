import pytest
from fastapi import HTTPException

from app.core.authorization import (
    TurmaAccessDeniedError,
    assert_matricula_access,
    assert_turma_access,
    enforce_matricula_access,
    enforce_turma_access,
    get_user_id,
    is_privileged,
)
from app.models.matricula import Matricula
from app.models.usuario import Usuario
from app.services.matricula_service import MatriculaNotFoundError
from app.services.turma_service import TurmaNotFoundError


def _criar_professor(db_session, email: str) -> Usuario:
    professor = Usuario(nome="Professor Secundário", email=email, senha_hash="x", cargo=2)
    db_session.add(professor)
    db_session.commit()
    db_session.refresh(professor)
    return professor


class TestHelpers:
    def test_is_privileged_diretor_e_admin(self):
        assert is_privileged({"cargo": 1}) is True
        assert is_privileged({"cargo": 3}) is True
        assert is_privileged({"cargo": 2}) is False

    def test_get_user_id_converte_sub(self):
        assert get_user_id({"sub": "7"}) == 7
        assert get_user_id({}) == 0


class TestAssertTurmaAccess:
    def test_diretor_acessa_qualquer_turma(self, db_session, turma):
        assert assert_turma_access(db_session, turma.id_turma, {"sub": "999", "cargo": 1}).id_turma == turma.id_turma

    def test_administrativo_acessa_qualquer_turma(self, db_session, turma):
        assert assert_turma_access(db_session, turma.id_turma, {"sub": "999", "cargo": 3}).id_turma == turma.id_turma

    def test_professor_dono_acessa(self, db_session, turma, usuario_professor):
        user = {"sub": str(usuario_professor.id_usuario), "cargo": 2}
        assert assert_turma_access(db_session, turma.id_turma, user).id_turma == turma.id_turma

    def test_professor_terceiro_recebe_negado(self, db_session, turma):
        outro = _criar_professor(db_session, "terceiro1@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(TurmaAccessDeniedError):
            assert_turma_access(db_session, turma.id_turma, user)

    def test_turma_inexistente_recebe_not_found(self, db_session):
        with pytest.raises(TurmaNotFoundError):
            assert_turma_access(db_session, 9999, {"sub": "1", "cargo": 1})


class TestAssertMatriculaAccess:
    def test_professor_dono_acessa(self, db_session, matricula_ativa, usuario_professor):
        user = {"sub": str(usuario_professor.id_usuario), "cargo": 2}
        result = assert_matricula_access(db_session, matricula_ativa.id_matricula, user)
        assert result.id_matricula == matricula_ativa.id_matricula

    def test_professor_terceiro_recebe_negado(self, db_session, matricula_ativa):
        outro = _criar_professor(db_session, "terceiro2@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(TurmaAccessDeniedError):
            assert_matricula_access(db_session, matricula_ativa.id_matricula, user)

    def test_matricula_inexistente_recebe_not_found(self, db_session):
        with pytest.raises(MatriculaNotFoundError):
            assert_matricula_access(db_session, 9999, {"sub": "1", "cargo": 1})


class TestEnforceTurmaAccess:
    def test_negado_vira_403(self, db_session, turma):
        outro = _criar_professor(db_session, "terceiro3@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(HTTPException) as exc:
            enforce_turma_access(db_session, turma.id_turma, user)
        assert exc.value.status_code == 403

    def test_inexistente_vira_404(self, db_session):
        with pytest.raises(HTTPException) as exc:
            enforce_turma_access(db_session, 9999, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404


class TestEnforceMatriculaAccess:
    def test_matricula_inexistente_vira_404(self, db_session):
        with pytest.raises(HTTPException) as exc:
            enforce_matricula_access(db_session, 9999, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404

    def test_matricula_de_turma_inexistente_vira_404(self, db_session):
        matricula = Matricula(id_aluno=1, id_turma=9999, status=0)
        db_session.add(matricula)
        db_session.commit()
        db_session.refresh(matricula)
        with pytest.raises(HTTPException) as exc:
            enforce_matricula_access(db_session, matricula.id_matricula, {"sub": "1", "cargo": 1})
        assert exc.value.status_code == 404

    def test_terceiro_vira_403(self, db_session, matricula_ativa):
        outro = _criar_professor(db_session, "terceiro4@abaco.org.br")
        user = {"sub": str(outro.id_usuario), "cargo": 2}
        with pytest.raises(HTTPException) as exc:
            enforce_matricula_access(db_session, matricula_ativa.id_matricula, user)
        assert exc.value.status_code == 403
