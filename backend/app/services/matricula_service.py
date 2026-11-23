from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.matricula import Matricula
from app.models.turma import Turma
from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaUpdateSchema


class MatriculaNotFoundError(Exception):
    pass


class MatriculaHasDependenciesError(Exception):
    pass


class AlunoNotFoundForMatriculaError(Exception):
    pass


class TurmaNotFoundForMatriculaError(Exception):
    pass


class TurmaLotadaError(Exception):
    pass


class MatriculaDuplicadaError(Exception):
    pass


def _resolve_aluno(db: Session, aluno_id: int) -> None:
    from app.models.aluno import Aluno

    aluno = db.query(Aluno).filter(Aluno.id_aluno == aluno_id).first()
    if not aluno:
        raise AlunoNotFoundForMatriculaError


def _resolve_turma(db: Session, turma_id: int) -> None:
    from app.models.turma import Turma

    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundForMatriculaError


def _check_turma_lotada(db: Session, turma_id: int, exclude_id: int | None = None) -> None:
    from app.models.turma import Turma

    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if turma and turma.capacidade:
        query = db.query(Matricula).filter(
            Matricula.id_turma == turma_id, Matricula.status == 0
        )
        if exclude_id is not None:
            query = query.filter(Matricula.id_matricula != exclude_id)
        if query.count() >= turma.capacidade:
            raise TurmaLotadaError


def _get_turma_curso_id(db: Session, turma_id: int) -> int:
    from app.models.turma import Turma
    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundForMatriculaError
    return turma.id_curso


def _check_matricula_duplicada(db: Session, aluno_id: int, turma_id: int, exclude_id: int | None = None) -> None:
    from app.models.turma import Turma

    curso_id = _get_turma_curso_id(db, turma_id)
    turmas_mesmo_curso = db.query(Turma.id_turma).filter(Turma.id_curso == curso_id).subquery()

    query = db.query(Matricula).filter(
        Matricula.id_aluno == aluno_id,
        Matricula.id_turma.in_(turmas_mesmo_curso),
        Matricula.status == 0,
    )
    if exclude_id is not None:
        query = query.filter(Matricula.id_matricula != exclude_id)

    existing = query.first()
    if existing:
        raise MatriculaDuplicadaError


def create_matricula(db: Session, payload: MatriculaCreateSchema) -> Matricula:
    _resolve_aluno(db, payload.idAluno)
    _resolve_turma(db, payload.idTurma)
    _check_turma_lotada(db, payload.idTurma)
    _check_matricula_duplicada(db, payload.idAluno, payload.idTurma)

    matricula = Matricula(
        id_aluno=payload.idAluno,
        id_turma=payload.idTurma,
        data_matricula=payload.dataMatricula,
        status=payload.status,
    )
    db.add(matricula)
    db.commit()
    db.refresh(matricula)
    return matricula


def list_matriculas(db: Session) -> list[Matricula]:
    return db.query(Matricula).order_by(Matricula.id_matricula.desc()).all()


def list_matriculas_by_professor(db: Session, professor_id: int) -> list[Matricula]:
    return (
        db.query(Matricula)
        .join(Matricula.turma)
        .filter(Turma.id_professor == professor_id)
        .order_by(Matricula.id_matricula.desc())
        .all()
    )


def get_matricula_by_id(db: Session, matricula_id: int) -> Matricula:
    matricula = db.query(Matricula).filter(Matricula.id_matricula == matricula_id).first()
    if not matricula:
        raise MatriculaNotFoundError
    return matricula


def update_matricula(db: Session, matricula_id: int, payload: MatriculaUpdateSchema) -> Matricula:
    matricula = get_matricula_by_id(db, matricula_id)

    novo_aluno_id = payload.idAluno if payload.idAluno is not None else matricula.id_aluno
    nova_turma_id = payload.idTurma if payload.idTurma is not None else matricula.id_turma

    if payload.idAluno is not None:
        _resolve_aluno(db, novo_aluno_id)

    if payload.idTurma is not None:
        _resolve_turma(db, nova_turma_id)
        _check_turma_lotada(db, nova_turma_id, exclude_id=matricula_id)

    if novo_aluno_id != matricula.id_aluno or nova_turma_id != matricula.id_turma:
        _check_matricula_duplicada(db, novo_aluno_id, nova_turma_id, exclude_id=matricula_id)

    matricula.id_aluno = novo_aluno_id
    matricula.id_turma = nova_turma_id

    if payload.dataMatricula is not None:
        matricula.data_matricula = payload.dataMatricula

    if payload.status is not None:
        matricula.status = payload.status

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise MatriculaHasDependenciesError from exc

    db.refresh(matricula)
    return matricula


def delete_matricula(db: Session, matricula_id: int) -> None:
    matricula = get_matricula_by_id(db, matricula_id)
    db.delete(matricula)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise MatriculaHasDependenciesError from exc
