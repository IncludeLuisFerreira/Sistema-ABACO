class TestNotasRbac:
    def test_professor_acessa_notas_da_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/notas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 200

    def test_professor_nao_acessa_notas_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/notas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_nao_acessa_media_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/notas/media/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_acessa_matricula_da_propria_turma(
        self, api_client, matricula_ativa, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(
            f"/api/v1/notas/matricula/{matricula_ativa.id_matricula}", headers=headers
        )
        assert response.status_code == 200

    def test_professor_nao_acessa_matricula_de_outro(
        self, api_client, matricula_ativa, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(
            f"/api/v1/notas/matricula/{matricula_ativa.id_matricula}", headers=headers
        )
        assert response.status_code == 403

    def test_professor_nao_lanca_notas_em_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.post(
            "/api/v1/notas",
            headers=headers,
            json={"idTurma": turma.id_turma, "prova": 1, "notas": []},
        )
        assert response.status_code == 403
