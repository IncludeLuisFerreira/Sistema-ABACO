import pytest
from fastapi import HTTPException

from app.core.dependencies import decode_access_token
from app.core.security import create_access_token, create_reset_token


class TestDecodeAccessToken:
    def test_accepts_access_token(self):
        token = create_access_token(subject="1", cargo=2)
        assert decode_access_token(token)["cargo"] == 2

    def test_rejects_reset_token(self):
        token = create_reset_token(email="maria@abaco.org.br")
        with pytest.raises(HTTPException) as exc:
            decode_access_token(token)
        assert exc.value.status_code == 401


class TestResetTokenNaoAcessaRotas:
    def test_reset_token_rejeitado_em_matriculas_me(self, api_client):
        token = create_reset_token(email="maria@abaco.org.br")
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.get("/api/v1/matriculas/me", headers=headers)
        assert response.status_code == 401

    def test_reset_token_rejeitado_em_turma_por_id(self, api_client):
        token = create_reset_token(email="maria@abaco.org.br")
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.get("/api/v1/turmas/1", headers=headers)
        assert response.status_code == 401

    def test_professor_matriculas_me_apenas_suas(
        self, api_client, matricula_ativa, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/matriculas/me", headers=headers)
        assert response.status_code == 200
        assert [m["idMatricula"] for m in response.json()] == [matricula_ativa.id_matricula]

    def test_diretor_matriculas_me_todas(self, api_client, matricula_ativa, diretor_headers):
        response = api_client.get("/api/v1/matriculas/me", headers=diretor_headers)
        assert response.status_code == 200
        assert [m["idMatricula"] for m in response.json()] == [matricula_ativa.id_matricula]
