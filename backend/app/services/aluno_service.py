from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.aluno import Aluno
from app.schemas.aluno_schema import AlunoCreateSchema, AlunoUpdateSchema


class AlunoNotFoundError(Exception):
    pass


class AlunoHasDependenciesError(Exception):
    pass


def create_aluno(db: Session, payload: AlunoCreateSchema) -> Aluno:
    aluno = Aluno(
        nome=payload.nome,
        telefone=payload.telefone,
        data_nascimento=payload.dataNascimento,
        rua=payload.rua,
        bairro=payload.bairro,
        numero=payload.numero,
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno


def list_alunos(db: Session) -> list[Aluno]:
    return db.query(Aluno).order_by(Aluno.nome.asc()).all()


def get_aluno_by_id(db: Session, aluno_id: int) -> Aluno:
    aluno = db.query(Aluno).filter(Aluno.id_aluno == aluno_id).first()
    if not aluno:
        raise AlunoNotFoundError
    return aluno


def update_aluno(db: Session, aluno_id: int, payload: AlunoUpdateSchema) -> Aluno:
    aluno = get_aluno_by_id(db, aluno_id)
    aluno.nome = payload.nome
    aluno.telefone = payload.telefone
    aluno.data_nascimento = payload.dataNascimento
    aluno.rua = payload.rua
    aluno.bairro = payload.bairro
    aluno.numero = payload.numero

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AlunoHasDependenciesError from exc

    db.refresh(aluno)
    return aluno


def delete_aluno(db: Session, aluno_id: int) -> None:
    aluno = get_aluno_by_id(db, aluno_id)
    db.delete(aluno)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AlunoHasDependenciesError from exc
