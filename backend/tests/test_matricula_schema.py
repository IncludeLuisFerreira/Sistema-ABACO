import pytest
from pydantic import ValidationError

from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaUpdateSchema


class TestMatriculaCreateSchema:
    @pytest.mark.parametrize("status", [0, 1, 2])
    def test_status_validos_aceitos(self, status):
        assert MatriculaCreateSchema(idAluno=1, idTurma=1, status=status).status == status

    def test_status_omitido_assume_ativo(self):
        assert MatriculaCreateSchema(idAluno=1, idTurma=1).status == 0

    @pytest.mark.parametrize("status", [3, -1, None, True, 1.0, "1"])
    def test_status_invalido_rejeitado(self, status):
        with pytest.raises(ValidationError):
            MatriculaCreateSchema(idAluno=1, idTurma=1, status=status)


class TestMatriculaUpdateSchema:
    @pytest.mark.parametrize("status", [0, 1, 2])
    def test_status_validos_aceitos(self, status):
        assert MatriculaUpdateSchema(status=status).status == status

    def test_status_omitido_continua_none(self):
        assert MatriculaUpdateSchema().status is None

    @pytest.mark.parametrize("status", [3, -1, True, 1.0, "1"])
    def test_status_invalido_rejeitado(self, status):
        with pytest.raises(ValidationError):
            MatriculaUpdateSchema(status=status)
