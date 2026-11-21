from datetime import datetime

from sqlalchemy.orm import Session

from app.models.estoque import Estoque
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.services.dashboard_service import get_chart_academico, get_chart_logistica, get_kpis


class TestGetKpis:
    def test_returns_structure(self, db_session: Session):
        kpis = get_kpis(db_session)
        assert "total_alunos_ativos" in kpis
        assert "total_turmas_vigentes" in kpis
        assert "total_pedidos_pendentes" in kpis
        assert "total_estoque_critico" in kpis

    def test_all_values_are_integers(self, db_session: Session):
        kpis = get_kpis(db_session)
        for value in kpis.values():
            assert isinstance(value, int)


class TestGetChartAcademico:
    def test_returns_structure(self, db_session: Session):
        chart = get_chart_academico(db_session)
        assert "alunos_por_curso" in chart
        assert "status_matriculas" in chart
        assert isinstance(chart["alunos_por_curso"], list)
        assert isinstance(chart["status_matriculas"], list)


class TestGetChartLogistica:
    def test_returns_structure(self, db_session: Session):
        chart = get_chart_logistica(db_session)
        assert "consumo_mes_atual" in chart
        assert isinstance(chart["consumo_mes_atual"], list)

    def test_consumo_mes_atual_retorna_valores_positivos_ordenados(self, db_session: Session):
        item_maior = Estoque(
            nome_item="Resma A4",
            quantidade_disponivel=100,
            unidade="un",
            estoque_minimo=10,
        )
        item_menor = Estoque(
            nome_item="Caneta",
            quantidade_disponivel=100,
            unidade="un",
            estoque_minimo=10,
        )
        db_session.add_all([item_maior, item_menor])
        db_session.flush()

        agora = datetime.now()
        db_session.add_all(
            [
                MovimentacaoEstoque(
                    id_item_estoque=item_maior.id_item_estoque,
                    quantidade=-10,
                    tipo_movimentacao="baixa_manual",
                    justificativa="Uso em aula",
                    data_movimentacao=agora,
                ),
                MovimentacaoEstoque(
                    id_item_estoque=item_menor.id_item_estoque,
                    quantidade=-3,
                    tipo_movimentacao="pedido_aprovado",
                    justificativa="Pedido aprovado",
                    data_movimentacao=agora,
                ),
                MovimentacaoEstoque(
                    id_item_estoque=item_menor.id_item_estoque,
                    quantidade=-2,
                    tipo_movimentacao="baixa_manual",
                    justificativa="Uso adicional",
                    data_movimentacao=agora,
                ),
            ]
        )
        db_session.commit()

        chart = get_chart_logistica(db_session)
        consumo = chart["consumo_mes_atual"]

        assert consumo == [
            {"item": "Resma A4", "quantidade": 10},
            {"item": "Caneta", "quantidade": 5},
        ]
