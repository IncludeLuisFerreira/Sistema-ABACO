import pytest


class TestEstoqueEndpoints:
    def test_listar(self, seeded, admin_headers):
        response = seeded["client"].get("/api/v1/estoque", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_buscar_por_nome(self, seeded, professor_headers):
        response = seeded["client"].get("/api/v1/estoque/search?q=papel", headers=professor_headers)
        assert response.status_code == 200
        assert any("Papel" in item["nomeItem"] for item in response.json())

    def test_alertas(self, api_client, director_headers):
        api_client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Lápis", "quantidadeDisponivel": 1, "unidade": "un", "estoqueMinimo": 5},
            headers=director_headers,
        )
        response = api_client.get("/api/v1/estoque/alertas", headers=director_headers)
        assert response.status_code == 200
        assert any(item["nomeItem"] == "Lápis" for item in response.json())

    def test_get_por_id(self, seeded, admin_headers):
        estoque_id = seeded["estoque"]["idItemEstoque"]
        response = seeded["client"].get(f"/api/v1/estoque/{estoque_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["idItemEstoque"] == estoque_id

    def test_get_inexistente_retorna_404(self, api_client, admin_headers):
        assert api_client.get("/api/v1/estoque/9999", headers=admin_headers).status_code == 404

    def test_create_sucesso(self, api_client, director_headers):
        response = api_client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Caneta", "quantidadeDisponivel": 50, "unidade": "cx", "estoqueMinimo": 10},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["nomeItem"] == "Caneta"

    def test_create_duplicado_levanta_erro_nao_tratado(self, seeded, director_headers):
        # O router não trata EstoqueAlreadyExistsError; a exceção escapa ao handler.
        from app.services.estoque_service import EstoqueAlreadyExistsError

        with pytest.raises(EstoqueAlreadyExistsError):
            seeded["client"].post(
                "/api/v1/estoque",
                json={"nomeItem": "papel a4", "quantidadeDisponivel": 1},
                headers=director_headers,
            )

    def test_update_sucesso(self, seeded, director_headers):
        estoque_id = seeded["estoque"]["idItemEstoque"]
        response = seeded["client"].put(
            f"/api/v1/estoque/{estoque_id}",
            json={"nomeItem": "Papel A4 Premium"},
            headers=director_headers,
        )
        assert response.status_code == 200
        assert response.json()["nomeItem"] == "Papel A4 Premium"

    def test_update_inexistente_retorna_404(self, api_client, director_headers):
        response = api_client.put("/api/v1/estoque/9999", json={"nomeItem": "X"}, headers=director_headers)
        assert response.status_code == 404

    def test_baixa_sucesso(self, seeded, admin_headers):
        estoque_id = seeded["estoque"]["idItemEstoque"]
        response = seeded["client"].put(
            f"/api/v1/estoque/{estoque_id}/baixa",
            json={"quantidade": 3, "justificativa": "uso interno"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["quantidadeDisponivel"] == 7

    def test_baixa_inexistente_retorna_404(self, api_client, admin_headers):
        response = api_client.put(
            "/api/v1/estoque/9999/baixa",
            json={"quantidade": 1, "justificativa": "x"},
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_baixa_saldo_insuficiente_retorna_400(self, seeded, admin_headers):
        estoque_id = seeded["estoque"]["idItemEstoque"]
        response = seeded["client"].put(
            f"/api/v1/estoque/{estoque_id}/baixa",
            json={"quantidade": 999, "justificativa": "excesso"},
            headers=admin_headers,
        )
        assert response.status_code == 400

    def test_delete_sucesso(self, api_client, director_headers):
        created = api_client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Borracha", "quantidadeDisponivel": 5},
            headers=director_headers,
        ).json()
        response = api_client.delete(f"/api/v1/estoque/{created['idItemEstoque']}", headers=director_headers)
        assert response.status_code == 200

    def test_delete_inexistente_retorna_404(self, api_client, director_headers):
        assert api_client.delete("/api/v1/estoque/9999", headers=director_headers).status_code == 404

    def test_delete_com_pedido_vinculado_retorna_409(self, seeded, director_headers):
        client = seeded["client"]
        estoque_id = seeded["estoque"]["idItemEstoque"]
        turma_id = seeded["turma"]["idTurma"]
        client.post(
            "/api/v1/pedidos",
            json={
                "idTurma": turma_id,
                "itens": [{"nomeItem": "Papel A4", "quantidade": 1, "idItemEstoque": estoque_id}],
            },
            headers=director_headers,
        )
        response = client.delete(f"/api/v1/estoque/{estoque_id}", headers=director_headers)
        assert response.status_code == 409
