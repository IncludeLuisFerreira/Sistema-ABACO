class TestTurmasEndpoints:
    def test_listar(self, seeded, admin_headers):
        response = seeded["client"].get("/api/v1/turmas", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_me_retorna_turmas_do_professor(self, seeded):
        response = seeded["client"].get("/api/v1/turmas/me", headers=seeded["professor_headers"])
        assert response.status_code == 200
        ids = [turma["idTurma"] for turma in response.json()]
        assert seeded["turma"]["idTurma"] in ids

    def test_me_de_outro_professor_sem_turmas(self, seeded):
        from app.core.security import create_access_token

        token = create_access_token(subject="9999", cargo=2)
        headers = {"Authorization": f"Bearer {token}"}
        response = seeded["client"].get("/api/v1/turmas/me", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_por_id_e_inexistente(self, seeded, admin_headers):
        client = seeded["client"]
        turma_id = seeded["turma"]["idTurma"]
        assert client.get(f"/api/v1/turmas/{turma_id}", headers=admin_headers).status_code == 200
        assert client.get("/api/v1/turmas/9999", headers=admin_headers).status_code == 404

    def test_create_sucesso(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json={"capacidade": 30, "idCurso": seeded["curso"]["idCurso"], "diasAula": "Ter"},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["capacidade"] == 30

    def test_create_curso_inexistente_retorna_400(self, api_client, director_headers):
        response = api_client.post(
            "/api/v1/turmas",
            json={"capacidade": 10, "idCurso": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_create_professor_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json={"capacidade": 10, "idCurso": seeded["curso"]["idCurso"], "idProfessor": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_update_sucesso(self, seeded, director_headers):
        turma_id = seeded["turma"]["idTurma"]
        response = seeded["client"].put(
            f"/api/v1/turmas/{turma_id}",
            json={"capacidade": 50, "diasAula": "Qua"},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["capacidade"] == 50

    def test_update_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.put("/api/v1/turmas/9999", json={"capacidade": 1}, headers=director_headers)
        assert response.status_code == 404

    def test_update_curso_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"idCurso": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_update_professor_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"idProfessor": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_delete_sucesso(self, seeded, director_headers):
        client = seeded["client"]
        turma = client.post(
            "/api/v1/turmas",
            json={"capacidade": 5, "idCurso": seeded["curso"]["idCurso"]},
            headers=director_headers,
        ).json()
        response = client.delete(f"/api/v1/turmas/{turma['idTurma']}", headers=director_headers)
        assert response.status_code == 200

    def test_delete_inexistente_retorna_404(self, api_client, director_headers):
        assert api_client.delete("/api/v1/turmas/9999", headers=director_headers).status_code == 404

    def test_delete_com_matricula_vinculada_retorna_409(self, seeded, director_headers):
        response = seeded["client"].delete(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            headers=director_headers,
        )
        assert response.status_code == 409
