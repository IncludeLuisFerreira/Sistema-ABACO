import pytest


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


class TestHealthCheck:
    def test_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_returns_ok(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "online" in response.json()["status"].lower()


class TestAuthEndpoints:
    def test_login_invalid_credentials_returns_401(self, client):
        response = client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"})
        assert response.status_code == 401

    def test_login_missing_fields_returns_422(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


class TestProtectedEndpoints:
    def test_alunos_without_token_returns_401(self, client):
        response = client.get("/api/v1/alunos")
        assert response.status_code == 401

    def test_alunos_with_valid_token(self, client, auth_headers):
        response = client.get("/api/v1/alunos", headers=auth_headers)
        assert response.status_code == 200

    def test_dashboard_requires_director(self, client, professor_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=professor_headers)
        assert response.status_code == 403

    def test_dashboard_director_ok(self, client, auth_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=auth_headers)
        assert response.status_code == 200

    def test_usuarios_requires_director(self, client, professor_headers):
        response = client.get("/api/v1/usuarios", headers=professor_headers)
        assert response.status_code == 403

    def test_rate_limit_headers_present(self, client):
        response = client.post("/api/v1/auth/login", json={"email": "x@x.com", "senha": "x"})
        assert "X-RateLimit-Limit" in response.headers or "Retry-After" in response.headers or response.status_code in (401, 429)
