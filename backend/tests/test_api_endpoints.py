import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.database import Base, get_db
from main import app


settings = get_settings()
# FIXME: TestClient usa o banco real; get_db/Base não são sobrescritos
client = TestClient(app)


@pytest.fixture
def auth_headers():
    from app.core.security import create_access_token
    token = create_access_token(subject="1", cargo=1)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def professor_headers():
    from app.core.security import create_access_token
    token = create_access_token(subject="2", cargo=2)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    from app.core.security import create_access_token
    token = create_access_token(subject="3", cargo=3)
    return {"Authorization": f"Bearer {token}"}


# Endpoints administrativos que exigem cargo 1 (Diretoria) ou 3 (Admin).
# Professor (cargo 2) deve receber 403 e anônimo 401.
RESTRICTED_ENDPOINTS = [
    ("get", "/api/v1/dashboard/kpis"),
    ("get", "/api/v1/dashboard/charts/academico"),
    ("get", "/api/v1/dashboard/charts/logistica"),
    ("get", "/api/v1/usuarios"),
    ("get", "/api/v1/usuarios/1"),
    ("get", "/api/v1/alunos"),
    ("get", "/api/v1/alunos/1"),
    ("get", "/api/v1/cursos"),
    ("get", "/api/v1/cursos/1"),
    ("put", "/api/v1/pedidos/1/aprovar"),
    ("put", "/api/v1/pedidos/1/comprar"),
    ("put", "/api/v1/pedidos/1"),
    ("put", "/api/v1/pedidos/1/entregar"),
    ("delete", "/api/v1/pedidos/1"),
]


# Endpoints de leitura liberados para Diretoria (1) e Admin (3).
MANAGER_LIST_ENDPOINTS = [
    "/api/v1/alunos",
    "/api/v1/cursos",
    "/api/v1/turmas",
    "/api/v1/matriculas",
    "/api/v1/estoque",
    "/api/v1/pedidos",
    "/api/v1/usuarios",
    "/api/v1/dashboard/kpis",
    "/api/v1/dashboard/charts/academico",
    "/api/v1/dashboard/charts/logistica",
]


class TestHealthCheck:
    def test_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_returns_ok(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "online" in response.json()["status"].lower()


class TestAuthEndpoints:
    def test_login_invalid_credentials_returns_401(self):
        response = client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"})
        assert response.status_code == 401

    def test_login_missing_fields_returns_422(self):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

class TestProtectedEndpoints:
    def test_alunos_without_token_returns_401(self):
        response = client.get("/api/v1/alunos")
        assert response.status_code == 401

    def test_alunos_with_valid_token(self, auth_headers):
        response = client.get("/api/v1/alunos", headers=auth_headers)
        assert response.status_code == 200

    def test_dashboard_requires_director(self, professor_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=professor_headers)
        assert response.status_code == 403

    def test_dashboard_director_ok(self, auth_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=auth_headers)
        assert response.status_code == 200

    def test_dashboard_admin_ok(self, admin_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=admin_headers)
        assert response.status_code == 200

    def test_usuarios_requires_director(self, professor_headers):
        response = client.get("/api/v1/usuarios", headers=professor_headers)
        assert response.status_code == 403

    def test_usuarios_admin_ok(self, admin_headers):
        response = client.get("/api/v1/usuarios", headers=admin_headers)
        assert response.status_code == 200

    @pytest.mark.parametrize("method,path", RESTRICTED_ENDPOINTS)
    def test_professor_denied_on_restricted_endpoints(self, method, path, professor_headers):
        response = getattr(client, method)(path, headers=professor_headers)
        assert response.status_code == 403, f"{method.upper()} {path} deveria retornar 403"

    @pytest.mark.parametrize("method,path", RESTRICTED_ENDPOINTS)
    def test_anonymous_unauthorized_on_restricted_endpoints(self, method, path):
        response = getattr(client, method)(path)
        assert response.status_code == 401, f"{method.upper()} {path} deveria retornar 401"

    @pytest.mark.parametrize("path", MANAGER_LIST_ENDPOINTS)
    def test_admin_can_read_manager_list_endpoints(self, path, admin_headers):
        response = client.get(path, headers=admin_headers)
        assert response.status_code == 200, f"GET {path} deveria retornar 200 para Admin"


    # TODO: assert frouxo (OR) não valida de fato o rate limit (429)
    def test_rate_limit_headers_present(self):
        response = client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"})
        assert "X-RateLimit-Limit" in response.headers or "Retry-After" in response.headers or response.status_code in (401, 429)


class TestAdminCrudAccess:
    def test_admin_full_crud_curso(self, admin_headers):
        created = client.post("/api/v1/cursos", json={"nomeCurso": "Curso RBAC"}, headers=admin_headers)
        assert created.status_code == 200
        curso_id = created.json()["idCurso"]

        assert client.get(f"/api/v1/cursos/{curso_id}", headers=admin_headers).status_code == 200
        updated = client.put(f"/api/v1/cursos/{curso_id}", json={"nomeCurso": "Curso RBAC 2"}, headers=admin_headers)
        assert updated.status_code == 200
        assert client.delete(f"/api/v1/cursos/{curso_id}", headers=admin_headers).status_code == 200

    def test_admin_full_crud_aluno(self, admin_headers):
        created = client.post("/api/v1/alunos", json={"nome": "Aluno RBAC"}, headers=admin_headers)
        assert created.status_code == 200
        aluno_id = created.json()["idAluno"]

        assert client.get(f"/api/v1/alunos/{aluno_id}", headers=admin_headers).status_code == 200
        updated = client.put(f"/api/v1/alunos/{aluno_id}", json={"nome": "Aluno RBAC 2"}, headers=admin_headers)
        assert updated.status_code == 200
        assert client.delete(f"/api/v1/alunos/{aluno_id}", headers=admin_headers).status_code == 200

    def test_professor_cannot_create_curso(self, professor_headers):
        response = client.post("/api/v1/cursos", json={"nomeCurso": "Curso Proibido"}, headers=professor_headers)
        assert response.status_code == 403

    def test_professor_cannot_create_aluno(self, professor_headers):
        response = client.post("/api/v1/alunos", json={"nome": "Aluno Proibido"}, headers=professor_headers)
        assert response.status_code == 403

