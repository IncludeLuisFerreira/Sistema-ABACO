from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.authorization import enforce_turma_access, require_turma_access
from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.models.turma import Turma
from app.schemas.presenca_schema import PresencaBatchSchema, PresencaResponseSchema
from app.services.presenca_service import create_or_update_presencas, list_presencas_by_turma

router = APIRouter(prefix="/api/v1/presencas", tags=["presencas"])


@router.post("")
def create_presencas(
    payload: PresencaBatchSchema,
    current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    enforce_turma_access(db, payload.idTurma, current_user)
    presencas = create_or_update_presencas(db, payload)
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
