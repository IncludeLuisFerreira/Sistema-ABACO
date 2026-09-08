from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, verify_cargo
from app.db.database import get_db
from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaResponseSchema, MatriculaUpdateSchema
from app.services.matricula_service import (
    AlunoNotFoundForMatriculaError,
    MatriculaDuplicadaError,
    MatriculaHasDependenciesError,
    MatriculaNotFoundError,
    TurmaLotadaError,
    TurmaNotFoundForMatriculaError,
    create_matricula,
    delete_matricula,
    get_matricula_by_id,
    list_matriculas,
    list_matriculas_by_professor,
    update_matricula,
)

router = APIRouter(prefix="/api/v1/matriculas", tags=["matriculas"])


@router.get("")
def read_matriculas(_current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [MatriculaResponseSchema.model_validate(m) for m in list_matriculas(db)]


@router.get("/me")
def read_matriculas_by_professor(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    cargo = int(current_user.get("cargo", 0))
    if cargo != 2:
        return [MatriculaResponseSchema.model_validate(m) for m in list_matriculas(db)]
    professor_id = int(current_user.get("sub", 0))
    return [MatriculaResponseSchema.model_validate(m) for m in list_matriculas_by_professor(db, professor_id)]


@router.get("/{matricula_id}")
def read_matricula(matricula_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        matricula = get_matricula_by_id(db, matricula_id)
    except MatriculaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matricula nao encontrada") from exc
    return MatriculaResponseSchema.model_validate(matricula)


@router.post("")
def create_matriculas(payload: MatriculaCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        matricula = create_matricula(db, payload)
    except AlunoNotFoundForMatriculaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno informado nao existe") from exc
    except TurmaNotFoundForMatriculaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turma informada nao existe") from exc
    except TurmaLotadaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turma esta lotada") from exc
    except MatriculaDuplicadaError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Aluno ja possui matricula ativa neste curso") from exc
    return MatriculaResponseSchema.model_validate(matricula)


@router.put("/{matricula_id}")
def update_matriculas(matricula_id: int, payload: MatriculaUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        matricula = update_matricula(db, matricula_id, payload)
    except MatriculaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matricula nao encontrada") from exc
    except AlunoNotFoundForMatriculaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aluno informado nao existe") from exc
    except TurmaNotFoundForMatriculaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turma informada nao existe") from exc
    except MatriculaHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nao foi possivel atualizar a matricula") from exc
    return MatriculaResponseSchema.model_validate(matricula)


@router.delete("/{matricula_id}")
def delete_matriculas(matricula_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_matricula(db, matricula_id)
    except MatriculaNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matricula nao encontrada") from exc
    except MatriculaHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nao e possivel excluir uma matricula que possui vinculos") from exc

    return {"detail": "Matricula excluida com sucesso"}
