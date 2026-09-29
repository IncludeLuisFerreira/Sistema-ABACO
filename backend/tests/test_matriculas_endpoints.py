class TestMatriculasEndpoints:
    def test_listar(self, seeded, admin_headers):
        response = seeded["client"].get("/api/v1/matriculas", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_me_professor_retorna_matriculas_da_sua_turma(self, seeded):
        response = seeded["client"].get("/api/v1/matriculas/me", headers=seeded["professor_headers"])
        assert response.status_code == 200
        ids = [matricula["idMatricula"] for matricula in response.json()]
        assert seeded["matricula"]["idMatricula"] in ids

    def test_me_nao_professor_retorna_todas(self, seeded):
        response = seeded["client"].get("/api/v1/matriculas/me", headers=seeded["director_headers"])
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_me_anonimo_retorna_401(self, api_client):
        assert api_client.get("/api/v1/matriculas/me").status_code == 401

    def test_me_cargo_invalido_retorna_403(self, seeded, guest_headers):
        response = seeded["client"].get("/api/v1/matriculas/me", headers=guest_headers)
        assert response.status_code == 403

    def test_get_por_id_e_inexistente(self, seeded, admin_headers):
        client = seeded["client"]
        matricula_id = seeded["matricula"]["idMatricula"]
        assert client.get(f"/api/v1/matriculas/{matricula_id}", headers=admin_headers).status_code == 200
        assert client.get("/api/v1/matriculas/9999", headers=admin_headers).status_code == 404

    def test_create_sucesso(self, seeded, director_headers):
        client = seeded["client"]
        aluno = client.post("/api/v1/alunos", json={"nome": "Aluno Dois"}, headers=director_headers).json()
        response = client.post(
            "/api/v1/matriculas",
            json={"idAluno": aluno["idAluno"], "idTurma": seeded["turma"]["idTurma"]},
            headers=director_headers,
        )
        assert response.status_code == 200

    def test_create_aluno_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/matriculas",
            json={"idAluno": 9999, "idTurma": seeded["turma"]["idTurma"]},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_create_turma_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/matriculas",
            json={"idAluno": seeded["aluno"]["idAluno"], "idTurma": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_create_duplicada_retorna_409(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/matriculas",
            json={"idAluno": seeded["aluno"]["idAluno"], "idTurma": seeded["turma"]["idTurma"]},
            headers=director_headers,
        )
        assert response.status_code == 409

    def test_create_turma_lotada_retorna_400(self, seeded, director_headers):
        client = seeded["client"]
        turma_id = seeded["turma"]["idTurma"]
        aluno2 = client.post("/api/v1/alunos", json={"nome": "Aluno Dois"}, headers=director_headers).json()
        assert client.post(
            "/api/v1/matriculas",
            json={"idAluno": aluno2["idAluno"], "idTurma": turma_id},
            headers=director_headers,
        ).status_code == 200

        aluno3 = client.post("/api/v1/alunos", json={"nome": "Aluno Tres"}, headers=director_headers).json()
        response = client.post(
            "/api/v1/matriculas",
            json={"idAluno": aluno3["idAluno"], "idTurma": turma_id},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_update_sucesso(self, seeded, director_headers):
        matricula_id = seeded["matricula"]["idMatricula"]
        response = seeded["client"].put(
            f"/api/v1/matriculas/{matricula_id}",
            json={"status": 1},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == 1

    def test_update_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.put("/api/v1/matriculas/9999", json={"status": 1}, headers=director_headers)
        assert response.status_code == 404

    def test_update_aluno_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/matriculas/{seeded['matricula']['idMatricula']}",
            json={"idAluno": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_update_turma_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/matriculas/{seeded['matricula']['idMatricula']}",
            json={"idTurma": 9999},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_delete_sucesso(self, seeded, director_headers):
        client = seeded["client"]
        aluno = client.post("/api/v1/alunos", json={"nome": "Aluno Delete"}, headers=director_headers).json()
        matricula = client.post(
            "/api/v1/matriculas",
            json={"idAluno": aluno["idAluno"], "idTurma": seeded["turma"]["idTurma"]},
            headers=director_headers,
        ).json()
        response = client.delete(f"/api/v1/matriculas/{matricula['idMatricula']}", headers=director_headers)
        assert response.status_code == 200

    def test_delete_inexistente_retorna_404(self, api_client, director_headers):
        assert api_client.delete("/api/v1/matriculas/9999", headers=director_headers).status_code == 404

    def test_delete_com_dependencias_retorna_409(self, seeded, director_headers):
        client = seeded["client"]
        matricula_id = seeded["matricula"]["idMatricula"]
        client.post(
            "/api/v1/notas",
            json={"idTurma": seeded["turma"]["idTurma"], "prova": 1, "notas": [{"idMatricula": matricula_id, "nota": 8.0}]},
            headers=director_headers,
        )
        response = client.delete(f"/api/v1/matriculas/{matricula_id}", headers=director_headers)
        assert response.status_code == 409
