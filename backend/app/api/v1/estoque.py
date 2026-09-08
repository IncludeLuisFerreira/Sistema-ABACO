from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.estoque_schema import (
    EstoqueAlertaResponseSchema,
    EstoqueBaixaSchema,
    EstoqueCreateSchema,
    EstoqueResponseSchema,
    EstoqueUpdateSchema,
)
from app.services.estoque_service import (
    EstoqueHasDependenciesError,
    EstoqueNotFoundError,
    EstoqueSaldoInsuficienteError,
    create_estoque,
    dar_baixa,
    delete_estoque,
    get_alertas,
    get_estoque_by_id,
    list_estoque,
    search_estoque_by_name,
    update_estoque,
)

router = APIRouter(prefix="/api/v1/estoque", tags=["estoque"])


@router.get("")
def read_estoque(_current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [EstoqueResponseSchema.model_validate(item) for item in list_estoque(db)]


@router.get("/search")
def search_estoque(q: str = Query(""), _current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [EstoqueResponseSchema.model_validate(item) for item in search_estoque_by_name(db, q)]


@router.get("/alertas")
def read_alertas_estoque(_current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [EstoqueAlertaResponseSchema.model_validate(item) for item in get_alertas(db)]


@router.get("/{estoque_id}")
def read_estoque_item(estoque_id: int, _current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    try:
        item = get_estoque_by_id(db, estoque_id)
    except EstoqueNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado") from exc
    return EstoqueResponseSchema.model_validate(item)


@router.post("")
def create_estoque_item(payload: EstoqueCreateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    item = create_estoque(db, payload)
    return EstoqueResponseSchema.model_validate(item)


@router.put("/{estoque_id}")
def update_estoque_item(estoque_id: int, payload: EstoqueUpdateSchema, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        item = update_estoque(db, estoque_id, payload)
    except EstoqueNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado") from exc
    except EstoqueHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o item de estoque") from exc
    return EstoqueResponseSchema.model_validate(item)


@router.delete("/{estoque_id}")
def delete_estoque_item(estoque_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_estoque(db, estoque_id)
    except EstoqueNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado") from exc
    except EstoqueHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível excluir um item de estoque que possui pedidos vinculados") from exc

    return {"detail": "Item de estoque excluído com sucesso"}


@router.put("/{estoque_id}/baixa")
def baixa_estoque_item(
    estoque_id: int,
    payload: EstoqueBaixaSchema,
    _current_user: dict = Depends(verify_cargo(1, 3)),
    db: Session = Depends(get_db),
):
    try:
        item = dar_baixa(db, estoque_id, payload.quantidade, payload.justificativa)
    except EstoqueNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estoque não encontrado") from exc
    except EstoqueSaldoInsuficienteError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Saldo insuficiente no estoque para esta operação")
    except EstoqueHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível dar baixa no estoque") from exc
    return EstoqueResponseSchema.model_validate(item)
