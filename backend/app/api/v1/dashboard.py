from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import verify_director_role
from app.db.database import get_db
from app.schemas.dashboard_schema import (
    ChartAcademicoResponse,
    ChartLogisticaResponse,
    KpisResponse,
)
from app.services.dashboard_service import (
    get_chart_academico,
    get_chart_logistica,
    get_kpis,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/kpis")
def read_kpis(
    _current_user: dict = Depends(verify_director_role),
    db: Session = Depends(get_db),
) -> KpisResponse:
    return KpisResponse(**get_kpis(db))


@router.get("/charts/academico")
def read_charts_academico(
    _current_user: dict = Depends(verify_director_role),
    db: Session = Depends(get_db),
) -> ChartAcademicoResponse:
    return ChartAcademicoResponse(**get_chart_academico(db))


@router.get("/charts/logistica")
def read_charts_logistica(
    _current_user: dict = Depends(verify_director_role),
    db: Session = Depends(get_db),
) -> ChartLogisticaResponse:
    return ChartLogisticaResponse(**get_chart_logistica(db))
