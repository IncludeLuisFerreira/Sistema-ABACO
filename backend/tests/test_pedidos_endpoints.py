from datetime import date

import pytest

from app.email import EmailDeliveryError
from app.models.estoque import Estoque
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.pedido import Pedido
from app.services import pedido_service


@pytest.fixture
def write_headers(seeded):
    """Token cujo subject é o id real da diretoria semeada (FK de pedido.id_usuario)."""
    return seeded["director_headers"]


def _criar_pedido(seeded, headers, quantidade: int = 1, item_id: int | None = None) -> dict:
    return seeded["client"].post(
        "/api/v1/pedidos",
        json={
            "idTurma": seeded["turma"]["idTurma"],
            "itens": [
                {
                    "nomeItem": "Papel A4",
                    "quantidade": quantidade,
                    "idItemEstoque": item_id or seeded["estoque"]["idItemEstoque"],
                }
            ],
        },
        headers=headers,
    ).json()


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

    def test_aprovar_somente_diretor(self, seeded, admin_headers, professor_headers, guest_headers):
        client = seeded["client"]
        pedido = _criar_pedido(seeded, seeded["director_headers"])

        assert client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar", headers=admin_headers
        ).status_code == 403
        assert client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar", headers=professor_headers
        ).status_code == 403
        assert client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar", headers=guest_headers
        ).status_code == 403

        aprovado = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert aprovado.status_code == 200
        assert aprovado.json()["status"] == 1

    def test_update_status_para_aprovado_tambem_e_exclusivo_do_diretor(
        self, seeded, admin_headers, professor_headers, guest_headers
    ):
        client = seeded["client"]
        pedido = _criar_pedido(seeded, seeded["director_headers"])

        for headers in (admin_headers, professor_headers, guest_headers):
            response = client.put(
                f"/api/v1/pedidos/{pedido['idPedido']}",
                json={"status": 1},
                headers=headers,
            )
            assert response.status_code == 403

        aprovado = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}",
            json={"status": 1},
            headers=seeded["director_headers"],
        )
        assert aprovado.status_code == 200
        assert aprovado.json()["status"] == 1

    def test_aprovar_deduz_estoque_e_registra_auditoria(self, seeded, db_session):
        client = seeded["client"]
        item_id = seeded["estoque"]["idItemEstoque"]
        pedido = _criar_pedido(seeded, seeded["director_headers"], quantidade=3)

        response = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert response.status_code == 200

        db_session.expire_all()
        estoque = db_session.get(Estoque, item_id)
        assert estoque.quantidade_disponivel == 7

        movimentacoes = (
            db_session.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.tipo_movimentacao == "pedido_aprovado")
            .all()
        )
        assert len(movimentacoes) == 1
        assert movimentacoes[0].quantidade == -3
        assert f"Pedido #{pedido['idPedido']}" in movimentacoes[0].justificativa
        assert "Papel A4" in movimentacoes[0].justificativa

    def test_saldo_insuficiente_reverte_aprovacao_sem_auditoria(self, seeded, db_session):
        client = seeded["client"]
        item = client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Item Rolamento", "quantidadeDisponivel": 1},
            headers=seeded["director_headers"],
        ).json()
        pedido = _criar_pedido(
            seeded,
            seeded["director_headers"],
            quantidade=5,
            item_id=item["idItemEstoque"],
        )

        response = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert response.status_code == 400

        db_session.expire_all()
        estoque = db_session.get(Estoque, item["idItemEstoque"])
        assert estoque.quantidade_disponivel == 1
        assert db_session.get(Pedido, pedido["idPedido"]).status == 0
        assert (
            db_session.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.tipo_movimentacao == "pedido_aprovado")
            .count()
            == 0
        )

    def test_aprovar_envia_email_ao_solicitante(self, seeded, monkeypatch):
        client = seeded["client"]
        pedido = _criar_pedido(seeded, seeded["professor_headers"], quantidade=2)
        chamadas = []

        def fake_send(to_email, pedido_id, data_aprovacao, itens):
            chamadas.append((to_email, pedido_id, data_aprovacao, itens))

        monkeypatch.setattr(pedido_service, "send_pedido_aprovado_email", fake_send)

        response = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert response.status_code == 200
        assert chamadas == [
            (
                "prof@abaco.org.br",
                pedido["idPedido"],
                date.today(),
                [("Papel A4", 2)],
            )
        ]

    def test_aprovacao_nao_envia_email_quando_baixa_falha(self, seeded, monkeypatch):
        client = seeded["client"]
        item = client.post(
            "/api/v1/estoque",
            json={"nomeItem": "Item Sem Saldo", "quantidadeDisponivel": 0},
            headers=seeded["director_headers"],
        ).json()
        pedido = _criar_pedido(
            seeded,
            seeded["director_headers"],
            quantidade=1,
            item_id=item["idItemEstoque"],
        )
        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        response = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert response.status_code == 400
        assert chamadas == []

    def test_falha_de_email_nao_reverte_aprovacao(self, seeded, monkeypatch, caplog):
        client = seeded["client"]
        pedido = _criar_pedido(seeded, seeded["director_headers"], quantidade=1)

        def fake_send(*args, **kwargs):
            raise EmailDeliveryError("provedor indisponível")

        monkeypatch.setattr(pedido_service, "send_pedido_aprovado_email", fake_send)

        response = client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 1
        assert "Falha ao enviar e-mail de aprovação" in caplog.text
        assert "provedor indisponível" not in response.text

    def test_aprovar_pedido_ja_aprovado_nao_reenvia_email(self, seeded, monkeypatch):
        client = seeded["client"]
        pedido = _criar_pedido(seeded, seeded["director_headers"], quantidade=1)
        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        assert client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        ).status_code == 200
        assert client.put(
            f"/api/v1/pedidos/{pedido['idPedido']}/aprovar",
            headers=seeded["director_headers"],
        ).status_code == 400
        assert len(chamadas) == 1
