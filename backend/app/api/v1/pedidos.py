from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import verify_cargo
from app.db.database import get_db
from app.schemas.pedido_schema import PedidoCompraSchema, PedidoCreateSchema, PedidoResponseSchema, PedidoUpdateSchema
from app.services.pedido_service import (
    PedidoCannotBeDeliveredError,
    PedidoHasDependenciesError,
    PedidoInvalidTransitionError,
    PedidoNotFoundError,
    TurmaNotFoundForPedidoError,
    aprovar_pedido,
    comprar_pedido,
    create_pedido,
    delete_pedido,
    entregar_pedido,
    get_pedido_by_id,
    list_pedidos,
    update_pedido_status,
)

router = APIRouter(prefix="/api/v1/pedidos", tags=["pedidos"])


@router.get("")
def read_pedidos(_current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    return [PedidoResponseSchema.model_validate(pedido) for pedido in list_pedidos(db)]


@router.get("/{pedido_id}")
def read_pedido(pedido_id: int, _current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    try:
        pedido = get_pedido_by_id(db, pedido_id)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.post("")
def create_pedidos(payload: PedidoCreateSchema, current_user: dict = Depends(verify_cargo(1, 2, 3)), db: Session = Depends(get_db)):
    usuario_id = int(current_user.get("sub", 0))
    try:
        pedido = create_pedido(db, payload, usuario_id)
    except TurmaNotFoundForPedidoError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turma informada não existe") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.put("/{pedido_id}/aprovar")
def aprovar_pedido_endpoint(pedido_id: int, _current_user: dict = Depends(verify_cargo(1)), db: Session = Depends(get_db)):
    try:
        pedido = aprovar_pedido(db, pedido_id)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    except PedidoInvalidTransitionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível aprovar este pedido no momento")
    except PedidoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível aprovar o pedido") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.put("/{pedido_id}/comprar")
def comprar_pedido_endpoint(pedido_id: int, payload: PedidoCompraSchema, _current_user: dict = Depends(verify_cargo(1)), db: Session = Depends(get_db)):
    try:
        pedido = comprar_pedido(db, pedido_id, payload)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    except PedidoInvalidTransitionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível marcar este pedido como comprado no momento")
    except PedidoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível marcar o pedido como comprado") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.put("/{pedido_id}")
def update_pedidos(pedido_id: int, payload: PedidoUpdateSchema, _current_user: dict = Depends(verify_cargo(1)), db: Session = Depends(get_db)):
    try:
        pedido = update_pedido_status(db, pedido_id, payload)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    except PedidoInvalidTransitionError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível alterar o status deste pedido")
    except PedidoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível atualizar o pedido") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.put("/{pedido_id}/entregar")
def entregar_pedido_endpoint(pedido_id: int, _current_user: dict = Depends(verify_cargo(1)), db: Session = Depends(get_db)):
    try:
        pedido = entregar_pedido(db, pedido_id)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    except PedidoCannotBeDeliveredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pedido precisa estar com status 'Comprado' para ser entregue") from exc
    except PedidoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível entregar o pedido") from exc
    return PedidoResponseSchema.model_validate(pedido)


@router.delete("/{pedido_id}")
def delete_pedidos(pedido_id: int, _current_user: dict = Depends(verify_cargo(1, 3)), db: Session = Depends(get_db)):
    try:
        delete_pedido(db, pedido_id)
    except PedidoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado") from exc
    except PedidoHasDependenciesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não foi possível excluir o pedido") from exc

    return {"detail": "Pedido excluído com sucesso"}
