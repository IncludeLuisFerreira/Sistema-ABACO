from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import enforce_turma_access, require_turma_access
from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.models.turma import Turma
from app.schemas.presenca_schema import PresencaBatchSchema, PresencaResponseSchema
from app.services.presenca_service import (
    InvalidMatriculasError,
    create_or_update_presencas,
    list_presencas_by_turma,
)

router = APIRouter(prefix="/api/v1/presencas", tags=["presencas"])


def _matriculas_invalidas_detail(ids: list[int]) -> str:
    if len(ids) == 1:
        return f"A matrícula {ids[0]} não pertence à turma informada ou não está ativa."
    if len(ids) <= 3:
        lista = ", ".join(str(i) for i in ids[:-1]) + f" e {ids[-1]}"
        return f"As matrículas {lista} não pertencem à turma informada ou não estão ativas."
    return "Algumas matrículas informadas não pertencem à turma ou não estão ativas."


@router.post("")
def create_presencas(
    payload: PresencaBatchSchema,
    current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    enforce_turma_access(db, payload.idTurma, current_user)
    try:
        presencas = create_or_update_presencas(db, payload)
    except InvalidMatriculasError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_matriculas_invalidas_detail(exc.ids_invalidos),
        )
    return [PresencaResponseSchema.model_validate(p) for p in presencas]


@router.get("/turma/{turma_id}")
def read_presencas_by_turma(
    turma_id: int,
    data_aula: date | None = Query(None, alias="dataAula"),
    _turma: Turma = Depends(require_turma_access),
    db: Session = Depends(get_db),
):
    presencas = list_presencas_by_turma(db, turma_id, data_aula)
    return [PresencaResponseSchema.model_validate(p) for p in presencas]
