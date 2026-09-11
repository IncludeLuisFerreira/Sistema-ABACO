from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.turma import Turma
from app.schemas.nota_schema import MediaProvaSchema, NotaBatchSchema


class InvalidMatriculasError(Exception):
    pass


def _base_options():
    return [
        selectinload(Nota.matricula)
        .selectinload(Matricula.aluno),
        selectinload(Nota.matricula)
        .selectinload(Matricula.turma)
        .selectinload(Turma.curso),
    ]


def create_or_update_notas(db: Session, payload: NotaBatchSchema) -> list[Nota]:
    matriculas = db.query(Matricula).options(
        selectinload(Matricula.aluno),
        selectinload(Matricula.turma),
    ).filter(
        Matricula.id_turma == payload.idTurma,
        Matricula.status == 0,
    ).all()
    matriculas_por_id = {m.id_matricula for m in matriculas}

    ids_invalidos = [item.idMatricula for item in payload.notas if item.idMatricula not in matriculas_por_id]
    if ids_invalidos:
        raise InvalidMatriculasError(
            f"Matriculas {ids_invalidos} nao pertencem a turma informada ou nao estao ativas."
        )

    criadas: list[Nota] = []

    # FIXME: N+1 — consulta Nota dentro do loop; carregar todas de uma vez
    for item in payload.notas:
        nota = db.query(Nota).filter(
            Nota.id_matricula == item.idMatricula,
            Nota.prova == payload.prova,
        ).first()

        if nota:
            nota.nota = item.nota
        else:
            nota = Nota(
                id_matricula=item.idMatricula,
                prova=payload.prova,
                nota=item.nota,
            )
            db.add(nota)
        criadas.append(nota)

    db.commit()
    for n in criadas:
        db.refresh(n)
    return criadas


def list_notas_by_matricula(db: Session, matricula_id: int) -> list[Nota]:
    return db.query(Nota).options(*_base_options()).filter(
        Nota.id_matricula == matricula_id
    ).order_by(Nota.prova).all()


def list_notas_by_turma(db: Session, turma_id: int, prova: int | None = None) -> list[Nota]:
    query = db.query(Nota).options(*_base_options()).join(
        Matricula, Nota.id_matricula == Matricula.id_matricula
    ).filter(Matricula.id_turma == turma_id)
    if prova is not None:
        query = query.filter(Nota.prova == prova)
    return query.order_by(Nota.prova, Nota.id_nota).all()


def calcular_media_por_prova(db: Session, turma_id: int) -> list[MediaProvaSchema]:
    resultados = (
        db.query(
            Nota.prova,
            func.avg(Nota.nota).label("media"),
        )
        .join(Matricula, Nota.id_matricula == Matricula.id_matricula)
        .filter(Matricula.id_turma == turma_id, Nota.nota.isnot(None))
        .group_by(Nota.prova)
        .order_by(Nota.prova)
        .all()
    )
    return [MediaProvaSchema(prova=r.prova, media=round(float(r.media), 2) if r.media is not None else None) for r in resultados]
