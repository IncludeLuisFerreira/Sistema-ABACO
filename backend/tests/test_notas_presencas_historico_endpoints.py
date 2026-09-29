class TestNotasEndpoints:
    def test_create_sucesso(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/notas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "prova": 1,
                "notas": [{"idMatricula": seeded["matricula"]["idMatricula"], "nota": 8.5}],
            },
            headers=director_headers,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_create_prova_zero_retorna_422(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/notas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "prova": 0,
                "notas": [{"idMatricula": seeded["matricula"]["idMatricula"], "nota": 8.0}],
            },
            headers=director_headers,
        )
        assert response.status_code == 422

    def test_create_matricula_de_outra_turma_retorna_422(self, seeded, director_headers):
        client = seeded["client"]
        outro_aluno = client.post("/api/v1/alunos", json={"nome": "Alheio"}, headers=director_headers).json()
        outra_turma = client.post(
            "/api/v1/turmas",
            json={"capacidade": 5, "idCurso": seeded["curso"]["idCurso"]},
            headers=director_headers,
        ).json()
        outra_matricula = client.post(
            "/api/v1/matriculas",
            json={"idAluno": outro_aluno["idAluno"], "idTurma": outra_turma["idTurma"]},
            headers=director_headers,
        ).json()
        response = client.post(
            "/api/v1/notas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "prova": 1,
                "notas": [{"idMatricula": outra_matricula["idMatricula"], "nota": 7.0}],
            },
            headers=director_headers,
        )
        assert response.status_code == 422

    def test_listar_por_matricula(self, seeded):
        client = seeded["client"]
        professor_headers = seeded["professor_headers"]
        matricula_id = seeded["matricula"]["idMatricula"]
        client.post(
            "/api/v1/notas",
            json={"idTurma": seeded["turma"]["idTurma"], "prova": 1, "notas": [{"idMatricula": matricula_id, "nota": 9.0}]},
            headers=professor_headers,
        )
        response = client.get(f"/api/v1/notas/matricula/{matricula_id}", headers=professor_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_por_turma_com_e_sem_prova(self, seeded, admin_headers):
        client = seeded["client"]
        client.post(
            "/api/v1/notas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "prova": 2,
                "notas": [{"idMatricula": seeded["matricula"]["idMatricula"], "nota": 6.0}],
            },
            headers=admin_headers,
        )
        turma_id = seeded["turma"]["idTurma"]
        assert client.get(f"/api/v1/notas/turma/{turma_id}", headers=admin_headers).status_code == 200
        assert client.get(f"/api/v1/notas/turma/{turma_id}?prova=2", headers=admin_headers).status_code == 200

    def test_media_por_turma(self, seeded, admin_headers):
        client = seeded["client"]
        client.post(
            "/api/v1/notas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "prova": 1,
                "notas": [{"idMatricula": seeded["matricula"]["idMatricula"], "nota": 10.0}],
            },
            headers=admin_headers,
        )
        response = client.get(f"/api/v1/notas/media/turma/{seeded['turma']['idTurma']}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["idTurma"] == seeded["turma"]["idTurma"]


class TestPresencasEndpoints:
    def test_create_sucesso(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/presencas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "dataAula": "2026-01-10",
                "presencas": [{"idMatricula": seeded["matricula"]["idMatricula"], "presente": True}],
            },
            headers=director_headers,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_por_turma_com_e_sem_data(self, seeded):
        client = seeded["client"]
        professor_headers = seeded["professor_headers"]
        turma_id = seeded["turma"]["idTurma"]
        client.post(
            "/api/v1/presencas",
            json={
                "idTurma": turma_id,
                "dataAula": "2026-01-11",
                "presencas": [{"idMatricula": seeded["matricula"]["idMatricula"], "presente": False}],
            },
            headers=professor_headers,
        )
        assert client.get(f"/api/v1/presencas/turma/{turma_id}", headers=professor_headers).status_code == 200
        response = client.get(
            f"/api/v1/presencas/turma/{turma_id}?dataAula=2026-01-11",
            headers=professor_headers,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestHistoricoEndpoints:
    def test_historico_sucesso(self, seeded, admin_headers):
        client = seeded["client"]
        matricula_id = seeded["matricula"]["idMatricula"]
        client.post(
            "/api/v1/notas",
            json={"idTurma": seeded["turma"]["idTurma"], "prova": 1, "notas": [{"idMatricula": matricula_id, "nota": 7.5}]},
            headers=admin_headers,
        )
        client.post(
            "/api/v1/presencas",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "dataAula": "2026-01-12",
                "presencas": [{"idMatricula": matricula_id, "presente": True}],
            },
            headers=admin_headers,
        )
        response = client.get(f"/api/v1/historico/matricula/{matricula_id}", headers=admin_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["idMatricula"] == matricula_id
        assert body["percentualFrequencia"] == 100.0
        assert len(body["notas"]) == 1

    def test_historico_matricula_inexistente_retorna_404(self, api_client, admin_headers):
        response = api_client.get("/api/v1/historico/matricula/9999", headers=admin_headers)
        assert response.status_code == 404
