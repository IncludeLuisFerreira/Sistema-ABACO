from app.core.security import create_access_token


class TestUsuariosEndpoints:
    def test_list_retorna_usuarios(self, seeded, admin_headers):
        response = seeded["client"].get("/api/v1/usuarios", headers=admin_headers)
        assert response.status_code == 200
        assert any(u["email"] == "prof@abaco.org.br" for u in response.json())

    def test_create_sucesso(self, api_client, director_headers):
        response = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Novo", "email": "novo@abaco.org.br", "senha": "senha123", "cargo": 2},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["email"] == "novo@abaco.org.br"
        assert response.json()["cargo"] == 2

    def test_create_email_duplicado_retorna_erro(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/usuarios",
            json={"nome": "Duplicado", "email": "prof@abaco.org.br", "senha": "senha123", "cargo": 2},
            headers=director_headers,
        )
        assert response.status_code == 409

    def test_get_por_id(self, seeded, director_headers):
        usuario_id = seeded["professor"]["idUsuario"]
        response = seeded["client"].get(f"/api/v1/usuarios/{usuario_id}", headers=director_headers)
        assert response.status_code == 200
        assert response.json()["idUsuario"] == usuario_id

    def test_get_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.get("/api/v1/usuarios/9999", headers=director_headers)
        assert response.status_code == 404

    def test_update_sucesso(self, seeded, director_headers):
        usuario_id = seeded["professor"]["idUsuario"]
        response = seeded["client"].put(
            f"/api/v1/usuarios/{usuario_id}",
            json={"nome": "Professor Renomeado", "telefone": "11999999999", "cargo": 2},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Professor Renomeado"

    def test_update_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.put(
            "/api/v1/usuarios/9999",
            json={"nome": "X", "telefone": None, "cargo": 2},
            headers=director_headers,
        )
        assert response.status_code == 404

    def test_delete_proprio_usuario_retorna_403(self, seeded):
        usuario_id = seeded["professor"]["idUsuario"]
        token = create_access_token(subject=str(usuario_id), cargo=1)
        headers = {"Authorization": f"Bearer {token}"}
        response = seeded["client"].delete(f"/api/v1/usuarios/{usuario_id}", headers=headers)
        assert response.status_code == 403

    def test_delete_com_dependencia_retorna_409(self, seeded, admin_headers):
        # Professor tem turma vinculada -> FK impede exclusão.
        usuario_id = seeded["professor"]["idUsuario"]
        response = seeded["client"].delete(f"/api/v1/usuarios/{usuario_id}", headers=admin_headers)
        assert response.status_code == 409

    def test_delete_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.delete("/api/v1/usuarios/9999", headers=director_headers)
        assert response.status_code == 404

    def test_delete_sucesso(self, api_client, admin_headers):
        created = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Descartavel", "email": "descartavel@abaco.org.br", "senha": "senha123", "cargo": 2},
            headers=admin_headers,
        ).json()
        response = api_client.delete(f"/api/v1/usuarios/{created['idUsuario']}", headers=admin_headers)
        assert response.status_code == 200

    # --- Guarda anti-escalação: Admin (cargo 3) vs Diretoria (cargo 1) ---

    def test_admin_nao_pode_criar_usuario_cargo_1(self, api_client, admin_headers):
        response = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Quase Diretor", "email": "quase.diretor@abaco.org.br", "senha": "senha123", "cargo": 1},
            headers=admin_headers,
        )
        assert response.status_code == 403

    def test_admin_nao_pode_editar_usuario_cargo_1(self, seeded, admin_headers):
        usuario_id = seeded["director"]["idUsuario"]
        response = seeded["client"].put(
            f"/api/v1/usuarios/{usuario_id}",
            json={"nome": "Diretora Alterada", "telefone": None, "cargo": 2},
            headers=admin_headers,
        )
        assert response.status_code == 403

    def test_admin_nao_pode_definir_cargo_1_via_put(self, seeded, admin_headers):
        usuario_id = seeded["professor"]["idUsuario"]
        response = seeded["client"].put(
            f"/api/v1/usuarios/{usuario_id}",
            json={"nome": "Professor Promovido", "telefone": None, "cargo": 1},
            headers=admin_headers,
        )
        assert response.status_code == 403

    def test_admin_nao_pode_excluir_usuario_cargo_1(self, seeded, admin_headers):
        usuario_id = seeded["director"]["idUsuario"]
        response = seeded["client"].delete(f"/api/v1/usuarios/{usuario_id}", headers=admin_headers)
        assert response.status_code == 403

    def test_admin_nao_pode_alterar_proprio_cargo(self, api_client, director_headers):
        admin = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Admin", "email": "admin@abaco.org.br", "senha": "senha123", "cargo": 3},
            headers=director_headers,
        ).json()
        token = create_access_token(subject=str(admin["idUsuario"]), cargo=3)
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.put(
            f"/api/v1/usuarios/{admin['idUsuario']}",
            json={"nome": "Admin", "telefone": None, "cargo": 2},
            headers=headers,
        )
        assert response.status_code == 403

    def test_admin_pode_criar_e_editar_cargos_2_e_3(self, api_client, admin_headers):
        created = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Gestor", "email": "gestor@abaco.org.br", "senha": "senha123", "cargo": 3},
            headers=admin_headers,
        )
        assert created.status_code == 200
        usuario_id = created.json()["idUsuario"]
        response = api_client.put(
            f"/api/v1/usuarios/{usuario_id}",
            json={"nome": "Gestor Renomeado", "telefone": None, "cargo": 2},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["cargo"] == 2

    def test_diretoria_pode_criar_usuario_cargo_1(self, api_client, director_headers):
        response = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Novo Diretor", "email": "novo.diretor@abaco.org.br", "senha": "senha123", "cargo": 1},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["cargo"] == 1

    def test_diretoria_pode_editar_usuario_cargo_1(self, api_client, director_headers):
        created = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Diretor Editavel", "email": "diretor.editavel@abaco.org.br", "senha": "senha123", "cargo": 1},
            headers=director_headers,
        ).json()
        response = api_client.put(
            f"/api/v1/usuarios/{created['idUsuario']}",
            json={"nome": "Diretor Renomeado", "telefone": None, "cargo": 1},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Diretor Renomeado"

    def test_diretoria_pode_excluir_usuario_cargo_1(self, api_client, director_headers, diretor_headers):
        # diretor_headers carrega subject "999" (distinto do alvo criado com director_headers,
        # subject "1") para evitar que o bloqueio de auto-exclusão (subject == alvo) retorne 403.
        created = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Diretor Descartavel", "email": "diretor.descartavel@abaco.org.br", "senha": "senha123", "cargo": 1},
            headers=director_headers,
        ).json()
        response = api_client.delete(f"/api/v1/usuarios/{created['idUsuario']}", headers=diretor_headers)
        assert response.status_code == 200

    def test_admin_pode_editar_proprio_nome_telefone_mantendo_cargo_3(self, api_client, director_headers):
        admin = api_client.post(
            "/api/v1/usuarios",
            json={"nome": "Admin", "email": "admin.edita@abaco.org.br", "senha": "senha123", "cargo": 3},
            headers=director_headers,
        ).json()
        token = create_access_token(subject=str(admin["idUsuario"]), cargo=3)
        headers = {"Authorization": f"Bearer {token}"}
        response = api_client.put(
            f"/api/v1/usuarios/{admin['idUsuario']}",
            json={"nome": "Admin Atualizado", "telefone": "11988887777", "cargo": 3},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["nome"] == "Admin Atualizado"
        assert response.json()["cargo"] == 3
