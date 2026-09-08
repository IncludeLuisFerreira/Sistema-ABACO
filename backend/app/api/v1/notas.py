from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.nota_schema import MediaTurmaSchema, NotaBatchSchema, NotaResponseSchema
from app.services.nota_service import (
    InvalidMatriculasError,
    calcular_media_por_prova,
    create_or_update_notas,
    list_notas_by_matricula,
    list_notas_by_turma,
)

router = APIRouter(prefix="/api/v1/notas", tags=["notas"])


@router.post("")
def create_notas(
    payload: NotaBatchSchema,
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    if payload.prova < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="O numero da prova deve ser maior ou igual a 1.")
    try:
        notas = create_or_update_notas(db, payload)
    except InvalidMatriculasError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Algumas matrículas informadas não pertencem à turma")
    result = [NotaResponseSchema.model_validate(n) for n in notas]
    return result


@router.get("/matricula/{matricula_id}")
def read_notas_by_matricula(
    matricula_id: int,
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    notas = list_notas_by_matricula(db, matricula_id)
    return [NotaResponseSchema.model_validate(n) for n in notas]


@router.get("/turma/{turma_id}")
def read_notas_by_turma(
    turma_id: int,
    prova: int | None = Query(None),
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    notas = list_notas_by_turma(db, turma_id, prova)
    return [NotaResponseSchema.model_validate(n) for n in notas]


@router.get("/media/turma/{turma_id}")
def read_media_turma(
    turma_id: int,
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    medias = calcular_media_por_prova(db, turma_id)
    return MediaTurmaSchema(idTurma=turma_id, medias=medias)
