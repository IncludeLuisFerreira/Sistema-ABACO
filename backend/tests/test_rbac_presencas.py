class TestPresencasRbac:
    def test_professor_acessa_presencas_da_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/presencas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 200

    def test_professor_nao_acessa_presencas_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/presencas/turma/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_professor_nao_registra_presenca_em_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.post(
            "/api/v1/presencas",
            headers=headers,
            json={"idTurma": turma.id_turma, "dataAula": "2026-01-01", "presencas": []},
        )
        assert response.status_code == 403
