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
    def test_permite_cargo_autorizado(self, db_session, usuario):
        payload = verify_cargo(1, 3)(authorization=_bearer(create_access_token(subject=str(usuario.id_usuario), cargo=1)), db=db_session)
        assert payload["cargo"] == 1

    def test_nega_cargo_nao_autorizado(self, db_session, usuario_professor):
        with pytest.raises(HTTPException) as exc:
            verify_cargo(1)(authorization=_bearer(create_access_token(subject=str(usuario_professor.id_usuario), cargo=2)), db=db_session)
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
    def test_uses_current_role_and_first_access_flag(self, db_session, usuario_primeiro_acesso):
        token = create_access_token(subject=str(usuario_primeiro_acesso.id_usuario), cargo=2, primeiro_acesso=True)
        usuario_primeiro_acesso.cargo = 3
        usuario_primeiro_acesso.primeiro_acesso = False
        db_session.commit()

        payload = get_current_user(authorization=_bearer(token), db=db_session)
        assert payload["cargo"] == 3
        assert payload["primeiro_acesso"] is False

    def test_deleted_user_is_rejected(self, db_session, usuario):
        token = create_access_token(subject=str(usuario.id_usuario), cargo=1)
        db_session.delete(usuario)
        db_session.commit()

        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=_bearer(token), db=db_session)
        assert exc.value.status_code == 401

    def test_invalid_subject_is_rejected(self, db_session):
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=_bearer(create_access_token(subject="invalido", cargo=1)), db=db_session)
        assert exc.value.status_code == 401

    def test_retorna_payload_com_token_valido(self, db_session, usuario_professor):
        payload = get_current_user(authorization=_bearer(create_access_token(subject=str(usuario_professor.id_usuario), cargo=2)), db=db_session)
        assert payload["sub"] == str(usuario_professor.id_usuario)

    def test_nega_sem_token(self):
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=None)
        assert exc.value.status_code == 401


class TestAuthEdgesOnAdminEndpoints:
    def test_deleted_user_is_rejected_on_protected_routes(self, api_client, db_session, usuario):
        headers = {"Authorization": _bearer(create_access_token(subject=str(usuario.id_usuario), cargo=1))}
        assert api_client.get("/api/v1/cursos", headers=headers).status_code == 200
        db_session.delete(usuario)
        db_session.commit()

        response = api_client.get("/api/v1/cursos", headers=headers)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"
        response = api_client.post("/api/v1/auth/change-password", headers=headers, json={
            "senha_atual": "senha123", "nova_senha": "novaSenha1", "confirmar_senha": "novaSenha1",
        })
        assert response.status_code == 401

    def test_role_downgrade_takes_effect_with_same_token(self, api_client, db_session, usuario):
        headers = {"Authorization": _bearer(create_access_token(subject=str(usuario.id_usuario), cargo=1))}
        assert api_client.get("/api/v1/cursos", headers=headers).status_code == 200
        usuario.cargo = 2
        db_session.commit()

        assert api_client.get("/api/v1/cursos", headers=headers).status_code == 403

    def test_role_promotion_takes_effect_with_same_token(self, api_client, db_session, usuario_professor):
        headers = {"Authorization": _bearer(create_access_token(subject=str(usuario_professor.id_usuario), cargo=2))}
        assert api_client.get("/api/v1/cursos", headers=headers).status_code == 403
        usuario_professor.cargo = 3
        db_session.commit()

        assert api_client.get("/api/v1/cursos", headers=headers).status_code == 200

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
