import pytest
from sqlalchemy.orm import Session

from app.schemas.pedido_schema import ItemPedidoCreateSchema, PedidoCreateSchema, PedidoUpdateSchema
from app.services.pedido_service import (
    PedidoCannotBeDeliveredError,
    PedidoNotFoundError,
    create_pedido,
    get_pedido_by_id,
    list_pedidos,
    delete_pedido,
)


class TestCreatePedido:
    def test_creates_successfully(self, db_session: Session, turma, usuario):
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[ItemPedidoCreateSchema(nomeItem="Caneta", quantidade=10)],
        )
        result = create_pedido(db_session, payload, usuario.id_usuario)
        assert result.id_pedido is not None
        assert result.status == 0

    def test_creates_multiple_itens(self, db_session: Session, turma, usuario):
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[
                ItemPedidoCreateSchema(nomeItem="Caneta", quantidade=10),
                ItemPedidoCreateSchema(nomeItem="Papel", quantidade=5),
            ],
        )
        result = create_pedido(db_session, payload, usuario.id_usuario)
        assert len(result.itens) == 2


class TestListPedidos:
    def test_lists_all(self, db_session: Session, turma, usuario):
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[ItemPedidoCreateSchema(nomeItem="Caneta", quantidade=10)],
        )
        create_pedido(db_session, payload, usuario.id_usuario)

        results = list_pedidos(db_session)
        assert len(results) >= 1


class TestGetPedidoById:
    def test_finds_existing(self, db_session: Session, turma, usuario):
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[ItemPedidoCreateSchema(nomeItem="Caneta", quantidade=10)],
        )
        pedido = create_pedido(db_session, payload, usuario.id_usuario)
        result = get_pedido_by_id(db_session, pedido.id_pedido)
        assert result.id_pedido == pedido.id_pedido

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(PedidoNotFoundError):
            get_pedido_by_id(db_session, 9999)


class TestDeletePedido:
    def test_deletes_existing(self, db_session: Session, turma, usuario):
        payload = PedidoCreateSchema(
            idTurma=turma.id_turma,
            itens=[ItemPedidoCreateSchema(nomeItem="Caneta", quantidade=10)],
        )
        pedido = create_pedido(db_session, payload, usuario.id_usuario)
        delete_pedido(db_session, pedido.id_pedido)
        with pytest.raises(PedidoNotFoundError):
            get_pedido_by_id(db_session, pedido.id_pedido)

    def test_raises_for_nonexistent(self, db_session: Session):
        with pytest.raises(PedidoNotFoundError):
            delete_pedido(db_session, 9999)
