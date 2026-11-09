import pytest

from app.models.turma import Turma


def turma_payload(seeded, **overrides):
    data = {
        "capacidade": 30,
        "dataInicio": "2026-03-01",
        "dataFim": "2026-06-30",
        "idCurso": seeded["curso"]["idCurso"],
        "idProfessor": seeded["professor"]["idUsuario"],
        "diasAula": "1,3,5",
    }
    data.update(overrides)
    return data


def adicionar_matricula(client, headers, turma_id, nome):
    aluno = client.post("/api/v1/alunos", json={"nome": nome}, headers=headers).json()
    return client.post(
        "/api/v1/matriculas",
        json={"idAluno": aluno["idAluno"], "idTurma": turma_id},
        headers=headers,
    )


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
            json=turma_payload(seeded, diasAula="2,4"),
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["capacidade"] == 30
        assert response.json()["diasAula"] == "2,4"

    def test_create_com_avaliacoes_retorna_avaliacoes(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(
                seeded,
                avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}],
            ),
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"][0]["nome"] == "Prova 1"
        assert response.json()["avaliacoes"][0]["tipo"] == "prova"

    @pytest.mark.parametrize(
        "campo",
        ["idCurso", "idProfessor", "capacidade", "dataInicio", "dataFim", "diasAula"],
    )
    def test_create_sem_campo_obrigatorio_retorna_422(self, seeded, director_headers, campo):
        payload = turma_payload(seeded)
        payload.pop(campo)

        response = seeded["client"].post("/api/v1/turmas", json=payload, headers=director_headers)

        assert response.status_code == 422

    def test_create_capacidade_zero_retorna_422(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, capacidade=0),
            headers=director_headers,
        )
        assert response.status_code == 422

    def test_create_dias_aula_invalido_retorna_422(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, diasAula="Seg"),
            headers=director_headers,
        )
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "avaliacao",
        [
            {"nome": "", "tipo": "prova", "peso": 10},
            {"nome": "Prova 1", "tipo": "seminario", "peso": 10},
            {"nome": "Prova 1", "tipo": "prova", "peso": 0},
        ],
    )
    def test_create_avaliacao_invalida_retorna_422(self, seeded, director_headers, avaliacao):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, avaliacoes=[avaliacao]),
            headers=director_headers,
        )
        assert response.status_code == 422

    def test_create_data_fim_antes_da_inicio_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, dataInicio="2026-06-30", dataFim="2026-03-01"),
            headers=director_headers,
        )
        assert response.status_code == 400
        assert "data de início" in response.json()["detail"]

    def test_create_curso_inexistente_retorna_400(self, api_client, director_headers):
        response = api_client.post(
            "/api/v1/turmas",
            json={
                "capacidade": 10,
                "dataInicio": "2026-03-01",
                "dataFim": "2026-06-30",
                "idCurso": 9999,
                "idProfessor": 1,
                "diasAula": "1",
            },
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_create_professor_inexistente_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, idProfessor=9999),
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_create_professor_com_cargo_invalido_retorna_400(self, seeded, director_headers):
        response = seeded["client"].post(
            "/api/v1/turmas",
            json=turma_payload(seeded, idProfessor=seeded["director"]["idUsuario"]),
            headers=director_headers,
        )
        assert response.status_code == 400
        assert "cargo de Professor" in response.json()["detail"]

    def test_update_sucesso(self, seeded, director_headers):
        turma_id = seeded["turma"]["idTurma"]
        response = seeded["client"].put(
            f"/api/v1/turmas/{turma_id}",
            json={"capacidade": 50, "diasAula": "3"},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["capacidade"] == 50
        assert response.json()["diasAula"] == "3"

    def test_update_avaliacoes_null_mantem_avaliacoes(self, seeded, director_headers):
        client = seeded["client"]
        turma = client.post(
            "/api/v1/turmas",
            json=turma_payload(
                seeded,
                avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}],
            ),
            headers=director_headers,
        ).json()

        response = client.put(
            f"/api/v1/turmas/{turma['idTurma']}",
            json={"avaliacoes": None},
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"][0]["nome"] == "Prova 1"

    def test_update_avaliacoes_vazia_limpa_avaliacoes(self, seeded, director_headers):
        client = seeded["client"]
        turma = client.post(
            "/api/v1/turmas",
            json=turma_payload(
                seeded,
                avaliacoes=[{"nome": "Prova 1", "tipo": "prova", "peso": 10}],
            ),
            headers=director_headers,
        ).json()

        response = client.put(
            f"/api/v1/turmas/{turma['idTurma']}",
            json={"avaliacoes": []},
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"] == []

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

    def test_update_professor_com_cargo_invalido_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"idProfessor": seeded["director"]["idUsuario"]},
            headers=director_headers,
        )

        assert response.status_code == 400
        assert "cargo de Professor" in response.json()["detail"]

    def test_update_dias_aula_invalido_retorna_422(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"diasAula": "Seg"},
            headers=director_headers,
        )

        assert response.status_code == 422

    def test_update_capacidade_zero_retorna_422(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"capacidade": 0},
            headers=director_headers,
        )

        assert response.status_code == 422

    def test_update_avaliacao_invalida_retorna_422(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"avaliacoes": [{"nome": "", "tipo": "prova", "peso": 10}]},
            headers=director_headers,
        )

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "campo",
        ["idCurso", "idProfessor", "capacidade", "dataInicio", "dataFim", "diasAula"],
    )
    def test_update_limpando_campo_obrigatorio_retorna_400(self, seeded, director_headers, campo):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={campo: None},
            headers=director_headers,
        )
        assert response.status_code == 400
        assert campo in response.json()["detail"]

    def test_update_data_parcial_invertida_retorna_400(self, seeded, director_headers):
        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"dataInicio": "2026-07-01"},
            headers=director_headers,
        )
        assert response.status_code == 400

    def test_update_capacidade_abaixo_das_vagas_retorna_409(self, seeded, director_headers):
        client = seeded["client"]
        turma_id = seeded["turma"]["idTurma"]
        adicionar_matricula(client, director_headers, turma_id, "Segundo Aluno")

        response = client.put(
            f"/api/v1/turmas/{turma_id}",
            json={"capacidade": 1},
            headers=director_headers,
        )

        assert response.status_code == 409
        assert "2" in response.json()["detail"]

    def test_update_capacidade_igual_as_vagas_retorna_200(self, seeded, director_headers):
        client = seeded["client"]
        turma_id = seeded["turma"]["idTurma"]
        adicionar_matricula(client, director_headers, turma_id, "Segundo Aluno")

        response = client.put(
            f"/api/v1/turmas/{turma_id}",
            json={"capacidade": 2},
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["capacidade"] == 2

    def test_delete_sucesso(self, seeded, director_headers):
        client = seeded["client"]
        turma = client.post(
            "/api/v1/turmas",
            json=turma_payload(seeded, capacidade=5, diasAula="1"),
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

    def _gravar_avaliacoes_legadas(self, db_session, turma_id):
        turma = db_session.get(Turma, turma_id)
        turma.avaliacoes = [
            {"nome": "Legada", "tipo": "seminario", "peso": 10, "observacao": "antiga"}
        ]
        db_session.commit()

    def test_get_listar_preserva_avaliacoes_legadas(self, seeded, db_session, admin_headers):
        self._gravar_avaliacoes_legadas(db_session, seeded["turma"]["idTurma"])

        response = seeded["client"].get("/api/v1/turmas", headers=admin_headers)

        assert response.status_code == 200
        alvo = next(
            t for t in response.json() if t["idTurma"] == seeded["turma"]["idTurma"]
        )
        assert alvo["avaliacoes"][0]["tipo"] == "seminario"
        assert alvo["avaliacoes"][0]["observacao"] == "antiga"

    def test_get_por_id_preserva_avaliacoes_legadas(self, seeded, db_session, admin_headers):
        self._gravar_avaliacoes_legadas(db_session, seeded["turma"]["idTurma"])

        response = seeded["client"].get(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"][0]["tipo"] == "seminario"

    def test_update_legada_preserva_leitura_e_aplica_capacidade(
        self, seeded, db_session, director_headers
    ):
        self._gravar_avaliacoes_legadas(db_session, seeded["turma"]["idTurma"])

        response = seeded["client"].put(
            f"/api/v1/turmas/{seeded['turma']['idTurma']}",
            json={"capacidade": 25},
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"][0]["tipo"] == "seminario"

        db_session.expire_all()
        assert db_session.get(Turma, seeded["turma"]["idTurma"]).capacidade == 25

    def test_formatos_legados_mistos_nunca_retornam_500(
        self, seeded, db_session, admin_headers, director_headers
    ):
        turma_id = seeded["turma"]["idTurma"]
        legado = [
            None,
            "Prova",
            {"nome": "Legada", "tipo": "seminario", "peso": 10, "observacao": "antiga"},
        ]
        turma = db_session.get(Turma, turma_id)
        turma.avaliacoes = legado
        db_session.commit()

        lista = seeded["client"].get("/api/v1/turmas", headers=admin_headers)
        assert lista.status_code == 200
        alvo = next(t for t in lista.json() if t["idTurma"] == turma_id)
        assert alvo["avaliacoes"] == legado

        detalhe = seeded["client"].get(f"/api/v1/turmas/{turma_id}", headers=admin_headers)
        assert detalhe.status_code == 200
        assert detalhe.json()["avaliacoes"] == legado

        response = seeded["client"].put(
            f"/api/v1/turmas/{turma_id}",
            json={"capacidade": 25},
            headers=director_headers,
        )

        assert response.status_code == 200
        assert response.json()["avaliacoes"] == legado

        db_session.expire_all()
        atualizada = db_session.get(Turma, turma_id)
        assert atualizada.capacidade == 25
        assert atualizada.avaliacoes == legado
