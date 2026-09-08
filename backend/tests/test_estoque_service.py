import pytest
from sqlalchemy.orm import Session

from app.models.estoque import Estoque
from app.services.estoque_service import (
    EstoqueNotFoundError,
    EstoqueSaldoInsuficienteError,
    dar_baixa,
    get_alertas,
)


class TestDarBaixa:
    def test_deducao_valida(self, db_session: Session, estoque_item: Estoque):
        item_id = estoque_item.id_item_estoque
        result = dar_baixa(db_session, item_id, 30, "Consumo em aula")
        assert result.quantidade_disponivel == 70

    def test_deducao_exata(self, db_session: Session, estoque_item: Estoque):
        item_id = estoque_item.id_item_estoque
        result = dar_baixa(db_session, item_id, 100, "Uso total")
        assert result.quantidade_disponivel == 0

    def test_saldo_insuficiente_raises_error(self, db_session: Session, estoque_item: Estoque):
        item_id = estoque_item.id_item_estoque
        with pytest.raises(EstoqueSaldoInsuficienteError):
            dar_baixa(db_session, item_id, 200, "Tentativa de exceder")

    def test_item_inexistente_raises_error(self, db_session: Session):
        with pytest.raises(EstoqueNotFoundError):
            dar_baixa(db_session, 9999, 10, "Item nao existe")


class TestGetAlertas:
    def test_retorna_itens_abaixo_do_minimo(self, db_session: Session, estoque_item: Estoque):
        estoque_item.quantidade_disponivel = 5
        estoque_item.estoque_minimo = 10
        db_session.commit()

        alertas = get_alertas(db_session)
        assert len(alertas) == 1
        assert alertas[0].id_item_estoque == estoque_item.id_item_estoque

    def test_nao_retorna_itens_acima_do_minimo(self, db_session: Session, estoque_item: Estoque):
        estoque_item.quantidade_disponivel = 50
        estoque_item.estoque_minimo = 10
        db_session.commit()

        alertas = get_alertas(db_session)
        assert len(alertas) == 0

    def test_ignora_itens_sem_estoque_minimo(self, db_session: Session, estoque_item: Estoque):
        estoque_item.estoque_minimo = None
        estoque_item.quantidade_disponivel = 0
        db_session.commit()

        alertas = get_alertas(db_session)
        assert len(alertas) == 0
