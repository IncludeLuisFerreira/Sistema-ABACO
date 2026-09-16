from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.turma_schema import TurmaCreateSchema, TurmaResponseSchema, TurmaUpdateSchema
from app.services.turma_service import (
    CursoNotFoundForTurmaError,
    ProfessorNotFoundForTurmaError,
    TurmaHasDependenciesError,
    TurmaNotFoundError,
    create_turma,
    delete_turma,
    get_turma_by_id,
    list_turmas,
    list_turmas_by_professor,
    update_turma,
)

router = APIRouter(prefix="/api/v1/turmas", tags=["turmas"])


@router.get("")
def read_turmas(_current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [TurmaResponseSchema.model_validate(turma) for turma in list_turmas(db)]


@router.get("/me")
def read_minhas_turmas(current_user: dict = Depends(verify_cargo(1, 2)), db: Session = Depends(get_db)):
    professor_id = int(current_user.get("sub", 0))
    return [TurmaResponseSchema.model_validate(turma) for turma in list_turmas_by_professor(db, professor_id)]


@router.get("/{turma_id}")
def read_turma(turma_id: int, _current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    try:
        turma = get_turma_by_id(db, turma_id)
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    return TurmaResponseSchema.model_validate(turma)


@router.post("")
def create_turmas(payload: TurmaCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        turma = create_turma(db, payload)
    except CursoNotFoundForTurmaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso informado não existe") from exc
    except ProfessorNotFoundForTurmaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Professor informado não existe") from exc
    return TurmaResponseSchema.model_validate(turma)


@router.put("/{turma_id}")
def update_turmas(turma_id: int, payload: TurmaUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        turma = update_turma(db, turma_id, payload)
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except CursoNotFoundForTurmaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Curso informado não existe") from exc
    except ProfessorNotFoundForTurmaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Professor informado não existe") from exc
    except TurmaHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar a turma") from exc
    return TurmaResponseSchema.model_validate(turma)


@router.delete("/{turma_id}")
def delete_turmas(turma_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_turma(db, turma_id)
    except TurmaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada") from exc
    except TurmaHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível excluir uma turma que possui matrículas ou pedidos vinculados") from exc

    return {"detail": "Turma excluída com sucesso"}
