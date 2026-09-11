from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.estoque import Estoque
from app.models.matricula import Matricula
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.pedido import Pedido
from app.models.turma import Turma


def get_kpis(db: Session) -> dict:
    total_alunos = db.query(func.count(Aluno.id_aluno)).scalar() or 0

    hoje = date.today()
    total_turmas = (
        db.query(func.count(Turma.id_turma))
        .filter(
            Turma.data_inicio <= hoje,
            (Turma.data_fim >= hoje) | (Turma.data_fim.is_(None)),
        )
        .scalar()
        or 0
    )

    total_pedidos_pendentes = (
        db.query(func.count(Pedido.id_pedido))
        .filter(Pedido.status == 0)
        .scalar()
        or 0
    )

    total_estoque_critico = (
        db.query(func.count(Estoque.id_item_estoque))
        .filter(
            Estoque.quantidade_disponivel <= Estoque.estoque_minimo,
            Estoque.estoque_minimo.isnot(None),
        )
        .scalar()
        or 0
    )

    return {
        "total_alunos_ativos": total_alunos,
        "total_turmas_vigentes": total_turmas,
        "total_pedidos_pendentes": total_pedidos_pendentes,
        "total_estoque_critico": total_estoque_critico,
    }


def get_chart_academico(db: Session) -> dict:
    alunos_por_curso = (
        db.query(
            Curso.nome_curso.label("curso"),
            func.count(func.distinct(Matricula.id_aluno)).label("quantidade"),
        )
        .select_from(Matricula)
        .join(Turma, Turma.id_turma == Matricula.id_turma)
        .join(Curso, Curso.id_curso == Turma.id_curso)
        .group_by(Curso.nome_curso)
        .order_by(Curso.nome_curso)
        .all()
    )

    status_matriculas = (
        db.query(
            Matricula.status,
            func.count(Matricula.id_matricula).label("quantidade"),
        )
        .group_by(Matricula.status)
        .order_by(Matricula.status)
        .all()
    )

    return {
        "alunos_por_curso": [
            {"curso": row.curso, "quantidade": row.quantidade}
            for row in alunos_por_curso
        ],
        "status_matriculas": [
            {"status": row.status, "quantidade": row.quantidade}
            for row in status_matriculas
        ],
    }


def get_chart_logistica(db: Session) -> dict:
    hoje = date.today()
    # TODO: cálculo manual de virada de mês/ano é frágil; usar dateutil/timedelta
    primeiro_dia_mes = hoje.replace(day=1)
    if hoje.month == 12:
        primeiro_dia_proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
    else:
        primeiro_dia_proximo_mes = hoje.replace(month=hoje.month + 1, day=1)

    consumo = (
        db.query(
            Estoque.nome_item.label("item"),
            func.sum(MovimentacaoEstoque.quantidade).label("quantidade"),
        )
        .select_from(MovimentacaoEstoque)
        .join(
            Estoque,
            Estoque.id_item_estoque == MovimentacaoEstoque.id_item_estoque,
        )
        .filter(
            MovimentacaoEstoque.tipo_movimentacao.in_(["baixa_manual", "pedido_aprovado"]),
            MovimentacaoEstoque.data_movimentacao >= primeiro_dia_mes,
            MovimentacaoEstoque.data_movimentacao < primeiro_dia_proximo_mes,
        )
        .group_by(Estoque.nome_item)
        .order_by(func.sum(MovimentacaoEstoque.quantidade).desc())
        .all()
    )

    return {
        "consumo_mes_atual": [
            {"item": row.item, "quantidade": row.quantidade}
            for row in consumo
        ],
    }
