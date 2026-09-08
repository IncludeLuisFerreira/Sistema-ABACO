from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.presenca import Presenca
from app.models.turma import Turma
from app.models.usuario import Usuario


class MatriculaNotFoundError(Exception):
    pass


def _calculate_frequencia(presencas: list[Presenca]) -> float | None:
    if not presencas:
        return None
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    return round((presentes / total) * 100, 1)


def get_historico_by_matricula(db: Session, matricula_id: int) -> dict:
    matricula = (
        db.query(Matricula)
        .filter(Matricula.id_matricula == matricula_id)
        .first()
    )
    if not matricula:
        raise MatriculaNotFoundError

    aluno = db.query(Aluno).filter(Aluno.id_aluno == matricula.id_aluno).first()
    if not aluno:
        raise MatriculaNotFoundError("Aluno vinculado à matrícula não encontrado")

    turma = (
        db.query(Turma)
        .filter(Turma.id_turma == matricula.id_turma)
        .first()
    )

    curso_nome = None
    professor_nome = None
    if turma:
        curso = db.query(Curso).filter(Curso.id_curso == turma.id_curso).first()
        if curso:
            curso_nome = curso.nome_curso
        if turma.id_professor:
            professor = (
                db.query(Usuario)
                .filter(Usuario.id_usuario == turma.id_professor)
                .first()
            )
            if professor:
                professor_nome = professor.nome

    notas = (
        db.query(Nota)
        .filter(Nota.id_matricula == matricula_id)
        .order_by(Nota.prova)
        .all()
    )
    presencas = (
        db.query(Presenca)
        .filter(Presenca.id_matricula == matricula_id)
        .order_by(Presenca.data_aula)
        .all()
    )

    frequencia = _calculate_frequencia(presencas)

    return {
        "id_matricula": matricula.id_matricula,
        "data_matricula": matricula.data_matricula,
        "status": matricula.status,
        "aluno": {
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento,
            "telefone": aluno.telefone,
        },
        "turma": {
            "id_turma": turma.id_turma if turma else None,
            "nome_curso": curso_nome,
            "nome_professor": professor_nome,
            "data_inicio": turma.data_inicio if turma else None,
            "data_fim": turma.data_fim if turma else None,
            "dias_aula": turma.dias_aula if turma else None,
        },
        "notas": [
            {"prova": n.prova, "nota": n.nota} for n in notas
        ],
        "presencas": [
            {"data_aula": p.data_aula, "presente": p.presente} for p in presencas
        ],
        "percentual_frequencia": frequencia,
    }
