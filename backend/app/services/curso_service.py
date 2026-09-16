from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.curso import Curso
from app.schemas.curso_schema import CursoCreateSchema, CursoUpdateSchema


class CursoNotFoundError(Exception):
    pass


class CursoHasDependenciesError(Exception):
    pass


def create_curso(db: Session, payload: CursoCreateSchema) -> Curso:
    curso = Curso(
        nome_curso=payload.nomeCurso,
    )
    db.add(curso)
    db.commit()
    db.refresh(curso)
    return curso


def list_cursos(db: Session) -> list[Curso]:
    return db.query(Curso).order_by(Curso.nome_curso.asc()).all()


def get_curso_by_id(db: Session, curso_id: int) -> Curso:
    curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not curso:
        raise CursoNotFoundError
    return curso


def update_curso(db: Session, curso_id: int, payload: CursoUpdateSchema) -> Curso:
    curso = get_curso_by_id(db, curso_id)
    curso.nome_curso = payload.nomeCurso

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CursoHasDependenciesError from exc

    db.refresh(curso)
    return curso


def delete_curso(db: Session, curso_id: int) -> None:
    curso = get_curso_by_id(db, curso_id)
    db.delete(curso)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CursoHasDependenciesError from exc
