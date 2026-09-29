from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.services.matricula_service import MatriculaNotFoundError
from app.services.turma_service import TurmaNotFoundError


ACCESS_DENIED_DETAIL = "Acesso negado. Você não tem permissão para acessar este recurso."


class TurmaAccessDeniedError(Exception):
    pass


def is_privileged(current_user: dict) -> bool:
    return int(current_user.get("cargo", 0) or 0) in (1, 3)


def get_user_id(current_user: dict) -> int:
    return int(current_user.get("sub", 0) or 0)


def assert_turma_access(db: Session, turma_id: int, current_user: dict) -> Turma:
    turma = db.query(Turma).filter(Turma.id_turma == turma_id).first()
    if not turma:
        raise TurmaNotFoundError
    if is_privileged(current_user) or get_user_id(current_user) == turma.id_professor:
        return turma
    raise TurmaAccessDeniedError


def assert_matricula_access(db: Session, matricula_id: int, current_user: dict) -> Matricula:
    matricula = db.query(Matricula).filter(Matricula.id_matricula == matricula_id).first()
    if not matricula:
        raise MatriculaNotFoundError
    assert_turma_access(db, matricula.id_turma, current_user)
    return matricula


def enforce_turma_access(db: Session, turma_id: int, current_user: dict) -> Turma:
    try:
        return assert_turma_access(db, turma_id, current_user)
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except TurmaAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED_DETAIL) from exc


def enforce_matricula_access(db: Session, matricula_id: int, current_user: dict) -> Matricula:
    try:
        return assert_matricula_access(db, matricula_id, current_user)
    except MatriculaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada") from exc
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except TurmaAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ACCESS_DENIED_DETAIL) from exc


def require_turma_access(
    turma_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Turma:
    return enforce_turma_access(db, turma_id, current_user)


def require_matricula_access(
    matricula_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Matricula:
    return enforce_matricula_access(db, matricula_id, current_user)
