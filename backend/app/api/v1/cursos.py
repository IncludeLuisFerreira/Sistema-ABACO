from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.curso_schema import CursoCreateSchema, CursoResponseSchema, CursoUpdateSchema
from app.services.curso_service import (
    CursoHasDependenciesError,
    CursoNotFoundError,
    create_curso,
    delete_curso,
    get_curso_by_id,
    list_cursos,
    update_curso,
)

router = APIRouter(prefix="/api/v1/cursos", tags=["cursos"])


@router.get("")
def read_cursos(_current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    return [CursoResponseSchema.model_validate(curso) for curso in list_cursos(db)]


@router.get("/{curso_id}")
def read_curso(curso_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        curso = get_curso_by_id(db, curso_id)
    except CursoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado") from exc
    return CursoResponseSchema.model_validate(curso)


@router.post("")
def create_cursos(payload: CursoCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    curso = create_curso(db, payload)
    return CursoResponseSchema.model_validate(curso)


@router.put("/{curso_id}")
def update_cursos(curso_id: int, payload: CursoUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        curso = update_curso(db, curso_id, payload)
    except CursoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado") from exc
    except CursoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o curso") from exc
    return CursoResponseSchema.model_validate(curso)


@router.delete("/{curso_id}")
def delete_cursos(curso_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_curso(db, curso_id)
    except CursoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado") from exc
    except CursoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível excluir um curso que possui turmas vinculadas") from exc

    return {"detail": "Curso excluído com sucesso"}
