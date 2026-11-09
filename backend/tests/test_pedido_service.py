import pytest
from sqlalchemy.orm import Session

from app.email import EmailDeliveryError
from app.models.estoque import Estoque
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.models.usuario import Usuario
from app.schemas.pedido_schema import ItemPedidoCreateSchema, PedidoCreateSchema, PedidoUpdateSchema
from app.services import pedido_service
from app.services.pedido_service import (
    PedidoCannotBeDeliveredError,
    PedidoInvalidTransitionError,
    PedidoNotFoundError,
    aprovar_pedido,
    create_pedido,
    get_pedido_by_id,
    list_pedidos,
    delete_pedido,
    update_pedido_status,
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


def _criar_pedido_com_estoque(
    db_session: Session,
    turma,
    usuario,
    estoque_item: Estoque,
    quantidade: int = 5,
):
    payload = PedidoCreateSchema(
        idTurma=turma.id_turma,
        itens=[
            ItemPedidoCreateSchema(
                nomeItem=estoque_item.nome_item,
                quantidade=quantidade,
                idItemEstoque=estoque_item.id_item_estoque,
            )
        ],
    )
    return create_pedido(db_session, payload, usuario.id_usuario)


class TestAprovarPedido:
    def test_deduz_estoque_registra_auditoria_e_envia_email(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch
    ):
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 5)
        chamadas = []

        def fake_send(to_email, pedido_id, data_aprovacao, itens):
            chamadas.append((to_email, pedido_id, itens))

        monkeypatch.setattr(pedido_service, "send_pedido_aprovado_email", fake_send)

        result = aprovar_pedido(db_session, pedido.id_pedido)

        assert result.status == 1
        db_session.refresh(estoque_item)
        assert estoque_item.quantidade_disponivel == 95

        movimentacao = (
            db_session.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.tipo_movimentacao == "pedido_aprovado")
            .one()
        )
        assert movimentacao.quantidade == -5
        assert f"Pedido #{pedido.id_pedido}" in movimentacao.justificativa
        assert estoque_item.nome_item in movimentacao.justificativa
        assert chamadas == [
            (usuario.email, pedido.id_pedido, [(estoque_item.nome_item, 5)])
        ]

    def test_update_status_para_aprovado_reutiliza_o_fluxo(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch
    ):
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 2)
        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        result = update_pedido_status(db_session, pedido.id_pedido, PedidoUpdateSchema(status=1))

        assert result.status == 1
        db_session.refresh(estoque_item)
        assert estoque_item.quantidade_disponivel == 98
        assert len(chamadas) == 1

    def test_saldo_insuficiente_reverte_tudo(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch
    ):
        estoque_item.quantidade_disponivel = 3
        db_session.commit()
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 5)

        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        with pytest.raises(PedidoInvalidTransitionError):
            aprovar_pedido(db_session, pedido.id_pedido)

        db_session.refresh(pedido)
        db_session.refresh(estoque_item)
        assert pedido.status == 0
        assert estoque_item.quantidade_disponivel == 3
        assert (
            db_session.query(MovimentacaoEstoque)
            .filter(MovimentacaoEstoque.tipo_movimentacao == "pedido_aprovado")
            .count()
            == 0
        )
        assert chamadas == []

    def test_pedido_ja_aprovado_nao_reenvia_email(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch
    ):
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 1)
        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        aprovar_pedido(db_session, pedido.id_pedido)

        with pytest.raises(PedidoInvalidTransitionError):
            aprovar_pedido(db_session, pedido.id_pedido)

        assert len(chamadas) == 1

    def test_solicitante_sem_email_nao_falha_e_loga(
        self, db_session: Session, turma, estoque_item, monkeypatch, caplog
    ):
        sem_email = Usuario(nome="Sem E-mail", email=None, senha_hash="x", cargo=2)
        db_session.add(sem_email)
        db_session.commit()
        db_session.refresh(sem_email)
        pedido = _criar_pedido_com_estoque(db_session, turma, sem_email, estoque_item, 1)
        chamadas = []
        monkeypatch.setattr(
            pedido_service,
            "send_pedido_aprovado_email",
            lambda *args, **kwargs: chamadas.append(args),
        )

        result = aprovar_pedido(db_session, pedido.id_pedido)

        assert result.status == 1
        assert chamadas == []
        assert "sem envio de e-mail" in caplog.text

    def test_falha_do_provedor_nao_reverte_aprovacao(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch, caplog
    ):
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 1)

        def fake_send(*args, **kwargs):
            raise EmailDeliveryError("provedor fora do ar")

        monkeypatch.setattr(pedido_service, "send_pedido_aprovado_email", fake_send)

        result = aprovar_pedido(db_session, pedido.id_pedido)

        assert result.status == 1
        assert "Falha ao enviar e-mail de aprovação" in caplog.text

    def test_erro_inesperado_no_email_nao_reverte_aprovacao(
        self, db_session: Session, turma, usuario, estoque_item, monkeypatch, caplog
    ):
        pedido = _criar_pedido_com_estoque(db_session, turma, usuario, estoque_item, 1)

        def fake_send(*args, **kwargs):
            raise RuntimeError("erro interno")

        monkeypatch.setattr(pedido_service, "send_pedido_aprovado_email", fake_send)

        result = aprovar_pedido(db_session, pedido.id_pedido)

        assert result.status == 1
        assert "Erro inesperado ao enviar e-mail de aprovação" in caplog.text
