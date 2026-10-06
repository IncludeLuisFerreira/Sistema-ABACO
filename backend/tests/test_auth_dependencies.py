from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.dependencies import get_current_user, verify_cargo
from app.core.security import create_access_token


def _bearer(token: str) -> str:
    return f"Bearer {token}"


def _expired_token(cargo: int = 1) -> str:
    return create_access_token(subject="1", cargo=cargo, expires_delta=timedelta(seconds=-10))


class TestVerifyCargoUnit:
    def test_permite_cargo_autorizado(self):
        payload = verify_cargo(1, 3)(authorization=_bearer(create_access_token(subject="1", cargo=3)))
        assert payload["cargo"] == 3

    def test_nega_cargo_nao_autorizado(self):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization=_bearer(create_access_token(subject="2", cargo=2)))
        assert exc.value.status_code == 403

    def test_nega_sem_header(self):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization=None)
        assert exc.value.status_code == 401

    def test_nega_formato_de_token_invalido(self):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization="Token abc")
        assert exc.value.status_code == 401

    def test_nega_token_expirado(self):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization=_bearer(_expired_token()))
        assert exc.value.status_code == 401

    def test_nega_token_malformado(self):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization=_bearer("token.invalido.123"))
        assert exc.value.status_code == 401


class TestGetCurrentUserUnit:
    def test_retorna_payload_com_token_valido(self):
        payload = get_current_user(authorization=_bearer(create_access_token(subject="7", cargo=2)))
        assert payload["sub"] == "7"

    def test_nega_sem_token(self):
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=None)
        assert exc.value.status_code == 401


class TestAuthEdgesOnAdminEndpoints:
    def test_usuarios_com_token_expirado_retorna_401(self, api_client):
        response = api_client.get("/api/v1/usuarios", headers={"Authorization": f"Bearer {_expired_token()}"})
        assert response.status_code == 401

    def test_usuarios_com_token_malformado_retorna_401(self, api_client):
        response = api_client.get("/api/v1/usuarios", headers={"Authorization": "Bearer nao-e-um-jwt"})
        assert response.status_code == 401

    def test_usuarios_com_header_malformado_retorna_401(self, api_client):
        response = api_client.get("/api/v1/usuarios", headers={"Authorization": "Token abc"})
        assert response.status_code == 401

    def test_dashboard_com_token_expirado_retorna_401(self, api_client):
        response = api_client.get("/api/v1/dashboard/kpis", headers={"Authorization": f"Bearer {_expired_token()}"})
        assert response.status_code == 401
