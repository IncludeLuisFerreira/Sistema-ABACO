from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.notificacao_schema import (
    MarcarTodasLidasResponseSchema,
    NotificacaoContagemSchema,
    NotificacaoResponseSchema,
)
from app.services.notificacao_service import (
    NotificacaoNotFoundError,
    contar_nao_lidas,
    list_notificacoes,
    marcar_como_lida,
    marcar_todas_como_lidas,
)

router = APIRouter(prefix="/api/v1/notificacoes", tags=["notificacoes"])


@router.get("")
def read_notificacoes(
    apenas_nao_lidas: bool = False,
    limite: int = Query(50, ge=1, le=50),
    offset: int = Query(0, ge=0),
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    notificacoes = list_notificacoes(
        db,
        int(_current_user["sub"]),
        apenas_nao_lidas=apenas_nao_lidas,
        limite=limite,
        offset=offset,
    )
    return [NotificacaoResponseSchema.model_validate(item) for item in notificacoes]


@router.get("/contagem")
def read_contagem(
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    nao_lidas = contar_nao_lidas(db, int(_current_user["sub"]))
    return NotificacaoContagemSchema.model_validate({"naoLidas": nao_lidas})


@router.patch("/{notificacao_id}/lida")
def marcar_lida(
    notificacao_id: int,
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    try:
        notificacao = marcar_como_lida(db, int(_current_user["sub"]), notificacao_id)
    except NotificacaoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        ) from exc
    return NotificacaoResponseSchema.model_validate(notificacao)


@router.post("/marcar-todas-lidas")
def marcar_todas_lidas(
    _current_user: dict = Depends(verify_cargo(1, 2, 3)),
    db: Session = Depends(get_db),
):
    atualizadas = marcar_todas_como_lidas(db, int(_current_user["sub"]))
    return MarcarTodasLidasResponseSchema.model_validate({"atualizadas": atualizadas})
