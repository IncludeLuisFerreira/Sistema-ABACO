class TestTurmasRbac:
    def test_professor_acessa_propria_turma(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=headers)
        assert response.status_code == 200
        assert response.json()["idTurma"] == turma.id_turma

    def test_professor_nao_acessa_turma_de_outro(
        self, api_client, turma, outro_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(outro_professor)
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=headers)
        assert response.status_code == 403

    def test_turma_inexistente_retorna_404(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas/9999", headers=headers)
        assert response.status_code == 404

    def test_diretor_acessa_turma_de_terceiro(self, api_client, turma, diretor_headers):
        response = api_client.get(f"/api/v1/turmas/{turma.id_turma}", headers=diretor_headers)
        assert response.status_code == 200

    def test_professor_nao_lista_todas_turmas(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas", headers=headers)
        assert response.status_code == 403

    def test_professor_lista_apenas_suas_turmas(
        self, api_client, turma, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/turmas/me", headers=headers)
        assert response.status_code == 200
        assert [t["idTurma"] for t in response.json()] == [turma.id_turma]


class TestMatriculasListagemRbac:
    def test_professor_nao_lista_todas_matriculas(
        self, api_client, usuario_professor, professor_headers_factory
    ):
        headers = professor_headers_factory(usuario_professor)
        response = api_client.get("/api/v1/matriculas", headers=headers)
        assert response.status_code == 403
