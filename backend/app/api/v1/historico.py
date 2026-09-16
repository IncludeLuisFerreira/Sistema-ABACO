from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.historico_schema import HistoricoResponse
from app.services.historico_service import (
    MatriculaNotFoundError,
    get_historico_by_matricula,
)

router = APIRouter(prefix="/api/v1/historico", tags=["historico"])


@router.get("/matricula/{matricula_id}")
def read_historico_by_matricula(
    matricula_id: int,
    _current_user: dict = Depends(verify_cargo(1, 3)),
    db: Session = Depends(get_db),
):
    try:
        data = get_historico_by_matricula(db, matricula_id)
    except MatriculaNotFoundError:
        # HACK: import local de HTTPException/status foge do padrão dos routers
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matricula nao encontrada.",
        )
    return HistoricoResponse.model_validate(data)
