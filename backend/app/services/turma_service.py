from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.turma import Turma
from app.schemas.turma_schema import TurmaCreateSchema, TurmaUpdateSchema


class TurmaNotFoundError(Exception):
    pass


class TurmaHasDependenciesError(Exception):
    pass


class CursoNotFoundForTurmaError(Exception):
    pass


class ProfessorNotFoundForTurmaError(Exception):
    pass


def _resolve_curso(db: Session, curso_id: int) -> None:
    from app.models.curso import Curso

    curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        raise CursoNotFoundForTurmaError


def _resolve_professor(db: Session, professor_id: int | None) -> None:
    if professor_id is None:
        return
    from app.models.usuario import Usuario

    professor = db.query(Usuario).filter(Usuario.id_usuario == professor_id).first()
    if not professor:
        raise ProfessorNotFoundForTurmaError


def create_turma(db: Session, payload: TurmaCreateSchema) -> Turma:
    _resolve_curso(db, payload.idCurso)
    _resolve_professor(db, payload.idProfessor)

    turma = Turma(
        capacidade=payload.capacidade,
        data_inicio=payload.dataInicio,
        data_fim=payload.dataFim,
        id_curso=payload.idCurso,
        id_professor=payload.idProfessor,
        dias_aula=payload.diasAula,
        avaliacoes=payload.avaliacoes,
    )
    db.add(turma)
    db.commit()
    db.refresh(turma)
    return turma


def list_turmas(db: Session) -> list[Turma]:
    return db.query(Turma).order_by(Turma.id_turma.desc()).all()


def list_turmas_by_professor(db: Session, professor_id: int) -> list[Turma]:
    return db.query(Turma).filter(Turma.id_professor == professor_id).order_by(Turma.id_turma.desc()).all()


def get_turma_by_id(db: Session, turma_id: int) -> Turma:
    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundError
    return turma


def update_turma(db: Session, turma_id: int, payload: TurmaUpdateSchema) -> Turma:
    turma = get_turma_by_id(db, turma_id)

    if payload.idCurso is not None:
        _resolve_curso(db, payload.idCurso)
        turma.id_curso = payload.idCurso

    if payload.idProfessor is not None:
        _resolve_professor(db, payload.idProfessor)
        turma.id_professor = payload.idProfessor

    if payload.capacidade is not None:
        turma.capacidade = payload.capacidade
    if payload.dataInicio is not None:
        turma.data_inicio = payload.dataInicio
    if payload.dataFim is not None:
        turma.data_fim = payload.dataFim
    if payload.diasAula is not None:
        turma.dias_aula = payload.diasAula
    if payload.avaliacoes is not None:
        turma.avaliacoes = payload.avaliacoes

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise TurmaHasDependenciesError from exc

    db.refresh(turma)
    return turma


def delete_turma(db: Session, turma_id: int) -> None:
    turma = get_turma_by_id(db, turma_id)
    db.delete(turma)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise TurmaHasDependenciesError from exc
