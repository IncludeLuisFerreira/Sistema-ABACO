import pytest


@pytest.fixture
def write_headers(seeded):
    """Token cujo subject é o id real da diretoria semeada (FK de pedido.id_usuario)."""
    return seeded["director_headers"]


class TestPedidosEndpoints:
    def test_listar(self, seeded, professor_headers):
        response = seeded["client"].get("/api/v1/pedidos", headers=professor_headers)
        assert response.status_code == 200

    def test_create_sucesso(self, seeded, write_headers):
        client = seeded["client"]
        response = client.post(
            "/api/v1/pedidos",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "itens": [
                    {"nomeItem": "Papel A4", "quantidade": 2, "idItemEstoque": seeded["estoque"]["idItemEstoque"]}
                ],
            },
            headers=write_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert len(body["itens"]) == 1

    def test_create_turma_inexistente_retorna_400(self, api_client, write_headers):
        response = api_client.post(
            "/api/v1/pedidos",
            json={"idTurma": 9999, "itens": [{"nomeItem": "X", "quantidade": 1}]},
            headers=write_headers,
        )
        assert response.status_code == 400

    def test_get_por_id_e_inexistente(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        assert client.get(f"/api/v1/pedidos/{created['idPedido']}", headers=write_headers).status_code == 200
        assert client.get("/api/v1/pedidos/9999", headers=write_headers).status_code == 404

    def test_ciclo_completo_aprovar_comprar_entregar(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "itens": [
                    {"nomeItem": "Papel A4", "quantidade": 1, "idItemEstoque": seeded["estoque"]["idItemEstoque"]}
                ],
            },
            headers=write_headers,
        ).json()
        pedido_id = created["idPedido"]
        item_id = created["itens"][0]["idItemPedido"]

        aprovado = client.put(f"/api/v1/pedidos/{pedido_id}/aprovar", headers=write_headers)
        assert aprovado.status_code == 200
        assert aprovado.json()["status"] == 1

        comprado = client.put(
            f"/api/v1/pedidos/{pedido_id}/comprar",
            json={"itens": [{"idItemPedido": item_id, "quantidade": 1}]},
            headers=write_headers,
        )
        assert comprado.status_code == 200
        assert comprado.json()["status"] == 2

        entregue = client.put(f"/api/v1/pedidos/{pedido_id}/entregar", headers=write_headers)
        assert entregue.status_code == 200
        assert entregue.json()["status"] == 3

    def test_aprovar_duas_vezes_retorna_400(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        assert client.put(f"/api/v1/pedidos/{created['idPedido']}/aprovar", headers=write_headers).status_code == 200
        second = client.put(f"/api/v1/pedidos/{created['idPedido']}/aprovar", headers=write_headers)
        assert second.status_code == 400

    def test_aprovar_inexistente_retorna_404(self, api_client, write_headers):
        assert api_client.put("/api/v1/pedidos/9999/aprovar", headers=write_headers).status_code == 404

    def test_comprar_antes_de_aprovar_retorna_400(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        response = client.put(
            f"/api/v1/pedidos/{created['idPedido']}/comprar",
            json={"itens": []},
            headers=write_headers,
        )
        assert response.status_code == 400

    def test_entregar_antes_de_comprar_retorna_400(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        response = client.put(f"/api/v1/pedidos/{created['idPedido']}/entregar", headers=write_headers)
        assert response.status_code == 400

    def test_update_status_invalido_retorna_400(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        response = client.put(
            f"/api/v1/pedidos/{created['idPedido']}",
            json={"status": 5},
            headers=write_headers,
        )
        assert response.status_code == 400

    def test_update_status_para_aprovado_retorna_200(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        response = client.put(
            f"/api/v1/pedidos/{created['idPedido']}",
            json={"status": 1},
            headers=write_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == 1

    def test_aprovar_saldo_insuficiente_retorna_400(self, seeded, write_headers):
        client = seeded["client"]
        item = client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Item Escasso", "quantidadeDisponivel": 1},
            headers=write_headers,
        ).json()
        pedido = client.post(
            "/api/v1/pedidos",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "itens": [{"nomeItem": "Item Escasso", "quantidade": 5, "idItemEstoque": item["idItemEstoque"]}],
            },
            headers=write_headers,
        ).json()
        response = client.put(f"/api/v1/pedidos/{pedido['idPedido']}/aprovar", headers=write_headers)
        assert response.status_code == 400

    def test_delete_sucesso(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={"idTurma": seeded["turma"]["idTurma"], "itens": []},
            headers=write_headers,
        ).json()
        response = client.delete(f"/api/v1/pedidos/{created['idPedido']}", headers=write_headers)
        assert response.status_code == 200

    def test_delete_inexistente_retorna_404(self, api_client, write_headers):
        assert api_client.delete("/api/v1/pedidos/9999", headers=write_headers).status_code == 404

    def test_delete_com_itens_usa_cascade(self, seeded, write_headers):
        client = seeded["client"]
        created = client.post(
            "/api/v1/pedidos",
            json={
                "idTurma": seeded["turma"]["idTurma"],
                "itens": [{"nomeItem": "Papel A4", "quantidade": 1}],
            },
            headers=write_headers,
        ).json()
        response = client.delete(f"/api/v1/pedidos/{created['idPedido']}", headers=write_headers)
        assert response.status_code == 200
