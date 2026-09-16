from sqlalchemy.orm import Session

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
