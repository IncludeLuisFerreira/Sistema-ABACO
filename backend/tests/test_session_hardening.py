import jwt
import pytest
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from app.core.config import INSECURE_DEFAULT_SECRET, Settings
from app.core.security import create_access_token
from app.models.usuario import Usuario
from main import app


def _login_professor(api_client):
    return api_client.post(
        "/api/v1/auth/login",
        json={"email": "prof@abaco.org.br", "senha": "senha123"},
    )


class TestProductionSecret:
    def test_producao_rejeita_secret_key_default(self):
        with pytest.raises(ValidationError):
            Settings(**{"APP_ENV": "production", "SECRET_KEY": INSECURE_DEFAULT_SECRET})

    def test_producao_rejeita_secret_key_curta(self):
        with pytest.raises(ValidationError):
            Settings(**{"APP_ENV": "production", "SECRET_KEY": "segredo-curto"})

    def test_producao_aceita_secret_key_forte_e_exige_cookie_secure(self):
        settings = Settings(**{"APP_ENV": "production", "SECRET_KEY": "x" * 32})

        assert settings.is_production is True
        assert settings.effective_session_cookie_secure is True

    def test_desenvolvimento_mantem_cookie_sem_secure(self):
        settings = Settings(**{"APP_ENV": "development"})

        assert settings.is_production is False
        assert settings.effective_session_cookie_secure is False


class TestCorsPolicy:
    def test_cors_restrito_a_metodos_e_headers_usados(self):
        cors = next(
            middleware
            for middleware in app.user_middleware
            if middleware.cls is CORSMiddleware
        )

        assert cors.kwargs["allow_methods"] == ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        assert cors.kwargs["allow_headers"] == ["Authorization", "Content-Type", "X-CSRF-Token"]
        assert cors.kwargs["allow_credentials"] is True


class TestSessionCookie:
    def test_login_define_cookie_httponly_e_csrf_legivel(self, seeded, api_client):
        response = _login_professor(api_client)

        assert response.status_code == 200
        set_cookies = response.headers.get_list("set-cookie")
        session_cookie = next(c for c in set_cookies if c.startswith("abaco_session="))
        csrf_cookie = next(c for c in set_cookies if c.startswith("abaco_csrf="))

        assert "HttpOnly" in session_cookie
        assert "SameSite=lax" in session_cookie
        assert "HttpOnly" not in csrf_cookie
        assert response.json()["access_token"]

    def test_cookie_autentica_get_sem_authorization_header(self, seeded, api_client):
        assert _login_professor(api_client).status_code == 200

        response = api_client.get("/api/v1/turmas/me")

        assert response.status_code == 200

    def test_post_autenticado_por_cookie_exige_csrf(self, seeded, api_client):
        login = _login_professor(api_client)
        csrf_token = login.cookies.get("abaco_csrf")
        payload = {
            "senha_atual": "senha123",
            "nova_senha": "novaSenha1",
            "confirmar_senha": "novaSenha1",
        }

        sem_csrf = api_client.post("/api/v1/auth/change-password", json=payload)
        assert sem_csrf.status_code == 403

        com_csrf = api_client.post(
            "/api/v1/auth/change-password",
            json=payload,
            headers={"X-CSRF-Token": csrf_token},
        )
        assert com_csrf.status_code == 200


class TestRevogacao:
    def test_logout_invalida_token_emitido_no_login(self, seeded, api_client):
        login = _login_professor(api_client)
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        assert api_client.get("/api/v1/turmas/me", headers=headers).status_code == 200

        logout = api_client.post("/api/v1/auth/logout", headers=headers)
        assert logout.status_code == 204

        assert api_client.get("/api/v1/turmas/me", headers=headers).status_code == 401

    def test_token_antigo_e_rejeitado_apos_incremento_de_versao(
        self, seeded, api_client, db_session
    ):
        login = _login_professor(api_client)
        token = login.json()["access_token"]
        usuario = (
            db_session.query(Usuario)
            .filter(Usuario.email == "prof@abaco.org.br")
            .first()
        )
        usuario.token_version = int(usuario.token_version or 0) + 1
        db_session.commit()

        response = api_client.get(
            "/api/v1/turmas/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401


class TestClaimsDoToken:
    def test_access_token_inclui_jti_iat_e_versao(self):
        token = create_access_token(
            subject="1",
            cargo=1,
            token_version=3,
        )
        payload = jwt.decode(token, options={"verify_signature": False})

        assert payload["jti"]
        assert payload["iat"] > 0
        assert payload["ver"] == 3
