from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.presenca_schema import PresencaBatchSchema, PresencaResponseSchema
from app.services.presenca_service import create_or_update_presencas, list_presencas_by_turma

router = APIRouter(prefix="/api/v1/presencas", tags=["presencas"])


@router.post("")
def create_presencas(
    payload: PresencaBatchSchema,
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    presencas = create_or_update_presencas(db, payload)
    return [PresencaResponseSchema.model_validate(p) for p in presencas]


@router.get("/turma/{turma_id}")
def read_presencas_by_turma(
    turma_id: int,
    data_aula: date | None = Query(None, alias="dataAula"),
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    presencas = list_presencas_by_turma(db, turma_id, data_aula)
    return [PresencaResponseSchema.model_validate(p) for p in presencas]
