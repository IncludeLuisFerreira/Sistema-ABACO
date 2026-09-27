import pytest
from fastapi import HTTPException
from app.core.dependencies import verify_cargo, verify_director_role, decode_access_token, get_current_user


class TestAuthorizationDependenciesUnit:
    """Testes unitários das dependências de autorização do FastAPI."""

    def test_verify_cargo_success_for_allowed_cargo(self, admin_token):
        auth_header = f"Bearer {admin_token}"
        dep = verify_cargo(1)
        payload = dep(authorization=auth_header)
        assert payload["cargo"] == 1

    def test_verify_cargo_forbidden_for_disallowed_cargo(self, common_user_token):
        auth_header = f"Bearer {common_user_token}"
        dep = verify_cargo(1)
        with pytest.raises(HTTPException) as exc_info:
            dep(authorization=auth_header)
        assert exc_info.value.status_code == 403
        assert "Acesso negado" in exc_info.value.detail

    def test_verify_cargo_unauthorized_when_no_token(self):
        dep = verify_cargo(1)
        with pytest.raises(HTTPException) as exc_info:
            dep(authorization=None)
        assert exc_info.value.status_code == 401

    def test_verify_cargo_unauthorized_when_expired_token(self, expired_token):
        auth_header = f"Bearer {expired_token}"
        dep = verify_cargo(1)
        with pytest.raises(HTTPException) as exc_info:
            dep(authorization=auth_header)
        assert exc_info.value.status_code == 401

    def test_verify_cargo_unauthorized_when_invalid_token(self):
        auth_header = "Bearer token.invalido.123"
        dep = verify_cargo(1)
        with pytest.raises(HTTPException) as exc_info:
            dep(authorization=auth_header)
        assert exc_info.value.status_code == 401

    def test_verify_director_role_success(self, admin_token):
        auth_header = f"Bearer {admin_token}"
        payload = verify_director_role(authorization=auth_header)
        assert payload["cargo"] == 1

    def test_verify_director_role_forbidden_for_professor(self, common_user_token):
        auth_header = f"Bearer {common_user_token}"
        with pytest.raises(HTTPException) as exc_info:
            verify_director_role(authorization=auth_header)
        assert exc_info.value.status_code == 403


class TestUsuariosEndpointsAdminAuth:
    """Testes de integração de autorização para as rotas /api/v1/usuarios."""

    def test_read_usuarios_admin_allowed(self, client, admin_headers):
        response = client.get("/api/v1/usuarios", headers=admin_headers)
        assert response.status_code == 200

    def test_read_usuarios_common_user_forbidden(self, client, common_user_headers):
        response = client.get("/api/v1/usuarios", headers=common_user_headers)
        assert response.status_code == 403

    def test_read_usuarios_anonymous_unauthorized(self, client):
        response = client.get("/api/v1/usuarios")
        assert response.status_code == 401

    def test_read_usuarios_expired_token_unauthorized(self, client, expired_headers):
        response = client.get("/api/v1/usuarios", headers=expired_headers)
        assert response.status_code == 401

    def test_read_usuarios_invalid_token_unauthorized(self, client, invalid_token_headers):
        response = client.get("/api/v1/usuarios", headers=invalid_token_headers)
        assert response.status_code == 401

    def test_read_usuario_by_id_common_user_forbidden(self, client, common_user_headers):
        response = client.get("/api/v1/usuarios/1", headers=common_user_headers)
        assert response.status_code == 403

    def test_create_usuario_common_user_forbidden(self, client, common_user_headers):
        payload = {
            "nome": "Novo User",
            "email": "novo@abaco.org.br",
            "senha": "senha123PassWord!",
            "cargo": 2,
        }
        response = client.post("/api/v1/usuarios", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_update_usuario_common_user_forbidden(self, client, common_user_headers):
        payload = {"nome": "Updated User"}
        response = client.put("/api/v1/usuarios/1", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_delete_usuario_common_user_forbidden(self, client, common_user_headers):
        response = client.delete("/api/v1/usuarios/1", headers=common_user_headers)
        assert response.status_code == 403


class TestDashboardEndpointsAdminAuth:
    """Testes de integração de autorização para as rotas /api/v1/dashboard."""

    def test_dashboard_kpis_admin_allowed(self, client, admin_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=admin_headers)
        assert response.status_code == 200

    def test_dashboard_kpis_common_user_forbidden(self, client, common_user_headers):
        response = client.get("/api/v1/dashboard/kpis", headers=common_user_headers)
        assert response.status_code == 403

    def test_dashboard_kpis_anonymous_unauthorized(self, client):
        response = client.get("/api/v1/dashboard/kpis")
        assert response.status_code == 401

    def test_dashboard_charts_academico_common_user_forbidden(self, client, common_user_headers):
        response = client.get("/api/v1/dashboard/charts/academico", headers=common_user_headers)
        assert response.status_code == 403

    def test_dashboard_charts_logistica_common_user_forbidden(self, client, common_user_headers):
        response = client.get("/api/v1/dashboard/charts/logistica", headers=common_user_headers)
        assert response.status_code == 403


class TestPedidosEndpointsAdminAuth:
    """Testes de integração para as rotas /api/v1/pedidos restritas a Diretor/Admin (cargo 1)."""

    def test_aprovar_pedido_common_user_forbidden(self, client, common_user_headers):
        response = client.put("/api/v1/pedidos/1/aprovar", headers=common_user_headers)
        assert response.status_code == 403

    def test_comprar_pedido_common_user_forbidden(self, client, common_user_headers):
        payload = {"fornecedor": "Fornecedor Teste", "valor_total": 100.0}
        response = client.put("/api/v1/pedidos/1/comprar", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_update_pedido_common_user_forbidden(self, client, common_user_headers):
        payload = {"observacao": "Update Test"}
        response = client.put("/api/v1/pedidos/1", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_entregar_pedido_common_user_forbidden(self, client, common_user_headers):
        response = client.put("/api/v1/pedidos/1/entregar", headers=common_user_headers)
        assert response.status_code == 403

    def test_aprovar_pedido_admin_allowed(self, client, admin_headers):
        response = client.put("/api/v1/pedidos/1/aprovar", headers=admin_headers)
        # Passed auth filter (404 means route allowed but pedido id 1 doesn't exist in fake db)
        assert response.status_code in (200, 404)


class TestOtherModulesAdminAuth:
    """Testes das mutações em outros módulos restritos a cargos 1 e 3 (negados para cargo 2 - professor)."""

    def test_create_aluno_professor_forbidden(self, client, common_user_headers):
        payload = {"nome": "Aluno Teste"}
        response = client.post("/api/v1/alunos", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_create_curso_professor_forbidden(self, client, common_user_headers):
        payload = {"nome_curso": "Curso Teste"}
        response = client.post("/api/v1/cursos", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_create_turma_professor_forbidden(self, client, common_user_headers):
        payload = {"capacidade": 20, "id_curso": 1, "id_professor": 2}
        response = client.post("/api/v1/turmas", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_create_matricula_professor_forbidden(self, client, common_user_headers):
        payload = {"id_aluno": 1, "id_turma": 1}
        response = client.post("/api/v1/matriculas", json=payload, headers=common_user_headers)
        assert response.status_code == 403

    def test_create_estoque_professor_forbidden(self, client, common_user_headers):
        payload = {"nome_item": "Item", "quantidade_disponivel": 10}
        response = client.post("/api/v1/estoque", json=payload, headers=common_user_headers)
        assert response.status_code == 403
