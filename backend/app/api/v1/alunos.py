from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.aluno_schema import AlunoCreateSchema, AlunoResponseSchema, AlunoUpdateSchema
from app.services.aluno_service import (
    AlunoHasDependenciesError,
    AlunoNotFoundError,
    create_aluno,
    delete_aluno,
    get_aluno_by_id,
    list_alunos,
    update_aluno,
)

router = APIRouter(prefix="/api/v1/alunos", tags=["alunos"])


@router.get("")
# TODO: listagem sem paginação retorna a tabela inteira
# REFACTOR: endpoints sem type hint de retorno
def read_alunos(_current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    return [AlunoResponseSchema.model_validate(aluno) for aluno in list_alunos(db)]


@router.get("/{aluno_id}")
def read_aluno(aluno_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        aluno = get_aluno_by_id(db, aluno_id)
    except AlunoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado") from exc
    return AlunoResponseSchema.model_validate(aluno)


@router.post("")
def create_alunos(payload: AlunoCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    aluno = create_aluno(db, payload)
    return AlunoResponseSchema.model_validate(aluno)


@router.put("/{aluno_id}")
def update_alunos(aluno_id: int, payload: AlunoUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        aluno = update_aluno(db, aluno_id, payload)
    except AlunoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado") from exc
    except AlunoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o aluno") from exc
    return AlunoResponseSchema.model_validate(aluno)


@router.delete("/{aluno_id}")
def delete_alunos(aluno_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_aluno(db, aluno_id)
    except AlunoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado") from exc
    except AlunoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível excluir um aluno que possui matrículas vinculadas") from exc

    return {"detail": "Aluno excluído com sucesso"}
