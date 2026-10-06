import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, create_first_access_token, hash_password, verify_password
from app.db.database import Base, get_db
from app.email import EmailDeliveryError
from app.models.usuario import Usuario
from main import app

SENHA_INICIAL = "senha123"
SENHA_NOVA = "novaSenha1"

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
client = TestClient(app)


@pytest.fixture(autouse=True)
def _database():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _create_usuario(email: str, primeiro_acesso: bool = True) -> Usuario:
    db = TestingSessionLocal()
    usuario = Usuario(
        nome="Usuario Teste",
        email=email,
        senha_hash=hash_password(SENHA_INICIAL),
        cargo=2,
        primeiro_acesso=primeiro_acesso,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    db.close()
    return usuario


def _get_usuario(email: str) -> Usuario:
    db = TestingSessionLocal()
    try:
        return db.query(Usuario).filter(Usuario.email == email).first()
    finally:
        db.close()


class TestLoginFirstAccess:
    def test_login_exposes_first_access_flag(self):
        _create_usuario("primeiro@abaco.org.br", primeiro_acesso=True)

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "primeiro@abaco.org.br", "senha": SENHA_INICIAL},
        )

        assert response.status_code == 200
        assert response.json()["usuario"]["primeiro_acesso"] is True

    def test_login_after_password_change_clears_flag(self):
        _create_usuario("comum@abaco.org.br", primeiro_acesso=False)

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "comum@abaco.org.br", "senha": SENHA_INICIAL},
        )

        assert response.status_code == 200
        assert response.json()["usuario"]["primeiro_acesso"] is False


class TestChangePasswordEndpoint:
    def test_changes_password_and_clears_flag(self):
        usuario = _create_usuario("trocar@abaco.org.br", primeiro_acesso=True)
        token = create_access_token(subject=str(usuario.id_usuario), cargo=2, primeiro_acesso=True)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/auth/change-password",
            headers=headers,
            json={"senha_atual": SENHA_INICIAL, "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )

        assert response.status_code == 200
        atualizado = _get_usuario("trocar@abaco.org.br")
        assert atualizado.primeiro_acesso is False
        assert verify_password(SENHA_NOVA, atualizado.senha_hash)

    def test_wrong_current_password_returns_400(self):
        usuario = _create_usuario("errada@abaco.org.br", primeiro_acesso=True)
        token = create_access_token(subject=str(usuario.id_usuario), cargo=2, primeiro_acesso=True)

        response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"senha_atual": "incorreta", "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )

        assert response.status_code == 400

    def test_requires_authentication(self):
        response = client.post(
            "/api/v1/auth/change-password",
            json={"senha_atual": SENHA_INICIAL, "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )

        assert response.status_code == 401


class TestFirstAccessEndpoint:
    def test_defines_password_with_valid_token(self):
        _create_usuario("token@abaco.org.br", primeiro_acesso=True)
        token = create_first_access_token(email="token@abaco.org.br")

        response = client.post(
            "/api/v1/auth/first-access",
            json={"token": token, "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )

        assert response.status_code == 200
        atualizado = _get_usuario("token@abaco.org.br")
        assert atualizado.primeiro_acesso is False
        assert verify_password(SENHA_NOVA, atualizado.senha_hash)

    def test_invalid_token_returns_400(self):
        response = client.post(
            "/api/v1/auth/first-access",
            json={"token": "invalido", "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )

        assert response.status_code == 400


class TestCreateUsuarioSendsFirstAccessEmail:
    def test_sends_email_to_new_user(self, monkeypatch):
        sent = {}
        monkeypatch.setattr(
            "app.api.v1.usuarios.send_first_access_email",
            lambda email, token: sent.update({"email": email, "token": token}),
        )
        token = create_access_token(subject="1", cargo=1)

        response = client.post(
            "/api/v1/usuarios",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nome": "Novo Usuario",
                "email": "novo@abaco.org.br",
                "senha": SENHA_INICIAL,
                "cargo": 2,
            },
        )

        assert response.status_code == 200
        assert response.json()["primeiro_acesso"] is True
        assert sent["email"] == "novo@abaco.org.br"
        assert sent["token"]

    def test_creates_user_even_when_email_fails(self, monkeypatch):
        def failing_send(email, token):
            raise EmailDeliveryError("falha simulada no envio")

        monkeypatch.setattr("app.api.v1.usuarios.send_first_access_email", failing_send)
        token = create_access_token(subject="1", cargo=1)

        response = client.post(
            "/api/v1/usuarios",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "nome": "Novo Usuario",
                "email": "falha@abaco.org.br",
                "senha": SENHA_INICIAL,
                "cargo": 2,
            },
        )

        assert response.status_code == 200
        assert response.json()["primeiro_acesso"] is True
        persistido = _get_usuario("falha@abaco.org.br")
        assert persistido is not None
        assert persistido.primeiro_acesso is True
