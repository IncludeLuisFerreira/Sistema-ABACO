import pytest


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
    def test_returns_ok(self, api_client):
        response = api_client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_returns_ok(self, api_client):
        response = api_client.get("/")
        assert response.status_code == 200
        assert "online" in response.json()["status"].lower()


class TestAuthEndpoints:
    def test_login_invalid_credentials_returns_401(self, api_client):
        response = api_client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"})
        assert response.status_code == 401

    def test_login_missing_fields_returns_422(self, api_client):
        response = api_client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


class TestProtectedEndpoints:
    def test_alunos_without_token_returns_401(self, api_client):
        response = api_client.get("/api/v1/alunos")
        assert response.status_code == 401

    def test_alunos_with_valid_token(self, api_client, director_headers):
        response = api_client.get("/api/v1/alunos", headers=director_headers)
        assert response.status_code == 200

    def test_dashboard_requires_director(self, api_client, professor_headers):
        response = api_client.get("/api/v1/dashboard/kpis", headers=professor_headers)
        assert response.status_code == 403

    def test_dashboard_director_ok(self, api_client, director_headers):
        response = api_client.get("/api/v1/dashboard/kpis", headers=director_headers)
        assert response.status_code == 200

    def test_dashboard_admin_ok(self, api_client, admin_headers):
        response = api_client.get("/api/v1/dashboard/kpis", headers=admin_headers)
        assert response.status_code == 200

    def test_usuarios_requires_director(self, api_client, professor_headers):
        response = api_client.get("/api/v1/usuarios", headers=professor_headers)
        assert response.status_code == 403

    def test_usuarios_admin_ok(self, api_client, admin_headers):
        response = api_client.get("/api/v1/usuarios", headers=admin_headers)
        assert response.status_code == 200

    @pytest.mark.parametrize("method,path", RESTRICTED_ENDPOINTS)
    def test_professor_denied_on_restricted_endpoints(self, api_client, method, path, professor_headers):
        response = getattr(api_client, method)(path, headers=professor_headers)
        assert response.status_code == 403, f"{method.upper()} {path} deveria retornar 403"

    @pytest.mark.parametrize("method,path", RESTRICTED_ENDPOINTS)
    def test_guest_denied_on_restricted_endpoints(self, api_client, method, path, guest_headers):
        response = getattr(api_client, method)(path, headers=guest_headers)
        assert response.status_code == 403, f"{method.upper()} {path} deveria retornar 403 para cargo 0"

    @pytest.mark.parametrize("method,path", RESTRICTED_ENDPOINTS)
    def test_anonymous_unauthorized_on_restricted_endpoints(self, api_client, method, path):
        response = getattr(api_client, method)(path)
        assert response.status_code == 401, f"{method.upper()} {path} deveria retornar 401"

    @pytest.mark.parametrize("path", MANAGER_LIST_ENDPOINTS)
    def test_admin_can_read_manager_list_endpoints(self, api_client, path, admin_headers):
        response = api_client.get(path, headers=admin_headers)
        assert response.status_code == 200, f"GET {path} deveria retornar 200 para Admin"

    @pytest.mark.parametrize("path", MANAGER_LIST_ENDPOINTS)
    def test_director_can_read_manager_list_endpoints(self, api_client, path, director_headers):
        response = api_client.get(path, headers=director_headers)
        assert response.status_code == 200, f"GET {path} deveria retornar 200 para Diretoria"

    def test_login_rate_limit_returns_429(self, api_client):
        from app.core.limiter import limiter

        limiter.enabled = True
        limiter._storage.reset()
        try:
            statuses = [
                api_client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"}).status_code
                for _ in range(6)
            ]
        finally:
            limiter.enabled = False
            limiter._storage.reset()

        assert 429 in statuses, f"esperava 429 após exceder 5/minute, obtido: {statuses}"


class TestAdminCrudAccess:
    def test_admin_full_crud_curso(self, api_client, admin_headers):
        created = api_client.post("/api/v1/cursos", json={"nomeCurso": "Curso RBAC"}, headers=admin_headers)
        assert created.status_code == 200
        curso_id = created.json()["idCurso"]

        assert api_client.get(f"/api/v1/cursos/{curso_id}", headers=admin_headers).status_code == 200
        updated = api_client.put(f"/api/v1/cursos/{curso_id}", json={"nomeCurso": "Curso RBAC 2"}, headers=admin_headers)
        assert updated.status_code == 200
        assert api_client.delete(f"/api/v1/cursos/{curso_id}", headers=admin_headers).status_code == 200

    def test_admin_full_crud_aluno(self, api_client, admin_headers):
        created = api_client.post("/api/v1/alunos", json={"nome": "Aluno RBAC"}, headers=admin_headers)
        assert created.status_code == 200
        aluno_id = created.json()["idAluno"]

        assert api_client.get(f"/api/v1/alunos/{aluno_id}", headers=admin_headers).status_code == 200
        updated = api_client.put(f"/api/v1/alunos/{aluno_id}", json={"nome": "Aluno RBAC 2"}, headers=admin_headers)
        assert updated.status_code == 200
        assert api_client.delete(f"/api/v1/alunos/{aluno_id}", headers=admin_headers).status_code == 200

    def test_professor_cannot_create_curso(self, api_client, professor_headers):
        response = api_client.post("/api/v1/cursos", json={"nomeCurso": "Curso Proibido"}, headers=professor_headers)
        assert response.status_code == 403

    def test_professor_cannot_create_aluno(self, api_client, professor_headers):
        response = api_client.post("/api/v1/alunos", json={"nome": "Aluno Proibido"}, headers=professor_headers)
        assert response.status_code == 403
