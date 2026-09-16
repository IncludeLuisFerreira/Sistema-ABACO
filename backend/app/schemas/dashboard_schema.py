from datetime import date

from pydantic import BaseModel


class KpisResponse(BaseModel):
    total_alunos_ativos: int
    total_turmas_vigentes: int
    total_pedidos_pendentes: int
    total_estoque_critico: int


class AlunosPorCurso(BaseModel):
    curso: str
    quantidade: int


class StatusMatriculas(BaseModel):
    status: int
    quantidade: int


class ChartAcademicoResponse(BaseModel):
    alunos_por_curso: list[AlunosPorCurso]
    status_matriculas: list[StatusMatriculas]


class ConsumoItem(BaseModel):
    item: str
    quantidade: int


class ChartLogisticaResponse(BaseModel):
    consumo_mes_atual: list[ConsumoItem]
