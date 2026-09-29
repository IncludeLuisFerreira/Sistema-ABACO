from app.core.security import create_reset_token


class TestAuthEndpoints:
    def test_login_sucesso(self, seeded, api_client):
        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "prof@abaco.org.br", "senha": "senha123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["usuario"]["cargo"] == 2
        assert body["access_token"]

    def test_login_senha_incorreta_retorna_401(self, seeded, api_client):
        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "prof@abaco.org.br", "senha": "senha-errada"},
        )
        assert response.status_code == 401

    def test_login_usuario_inexistente_retorna_401(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login",
            json={"email": "naoexiste@abaco.org.br", "senha": "qualquer"},
        )
        assert response.status_code == 401

    def test_forgot_password_email_cadastrado(self, seeded, api_client):
        response = api_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "prof@abaco.org.br"},
        )
        assert response.status_code == 200
        assert "recuperação" in response.json()["message"].lower()

    def test_forgot_password_email_nao_cadastrado_resposta_generica(self, api_client):
        response = api_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "naoexiste@abaco.org.br"},
        )
        assert response.status_code == 200
        assert "recuperação" in response.json()["message"].lower()

    def test_forgot_password_falha_envio_email_retorna_500(self, seeded, api_client, monkeypatch):
        import app.api.v1.auth as auth_module

        def send_boom(*_args, **_kwargs):
            raise RuntimeError("SMTP indisponível")

        monkeypatch.setattr(auth_module, "send_reset_email", send_boom)
        response = api_client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "prof@abaco.org.br"},
        )
        assert response.status_code == 500

    def test_reset_password_sucesso_e_login_com_nova_senha(self, seeded, api_client):
        token = create_reset_token(email="prof@abaco.org.br")
        response = api_client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "nova_senha": "novaSenha1", "confirmar_senha": "novaSenha1"},
        )
        assert response.status_code == 200

        login = api_client.post(
            "/api/v1/auth/login",
            json={"email": "prof@abaco.org.br", "senha": "novaSenha1"},
        )
        assert login.status_code == 200

    def test_reset_password_token_invalido_retorna_400(self, seeded, api_client):
        response = api_client.post(
            "/api/v1/auth/reset-password",
            json={"token": "token-invalido", "nova_senha": "novaSenha1", "confirmar_senha": "novaSenha1"},
        )
        assert response.status_code == 400

    def test_reset_password_senhas_divergentes_retorna_422(self, seeded, api_client):
        token = create_reset_token(email="prof@abaco.org.br")
        response = api_client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "nova_senha": "novaSenha1", "confirmar_senha": "outraSenha1"},
        )
        assert response.status_code == 422

    def test_reset_password_sem_numero_retorna_422(self, seeded, api_client):
        token = create_reset_token(email="prof@abaco.org.br")
        response = api_client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "nova_senha": "somenteletras", "confirmar_senha": "somenteletras"},
        )
        assert response.status_code == 422
