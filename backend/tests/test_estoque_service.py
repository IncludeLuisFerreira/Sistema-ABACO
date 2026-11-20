import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.estoque import Estoque
from app.schemas.estoque_schema import EstoqueCreateSchema, EstoqueUpdateSchema
from app.services.estoque_service import (
    EstoqueAlreadyExistsError,
    EstoqueNotFoundError,
    EstoqueSaldoInsuficienteError,
    create_estoque,
    dar_baixa,
    get_alertas,
    search_estoque_by_name,
    update_estoque,
)


class TestCreateEstoque:
    def test_normaliza_espacos(self, db_session: Session):
        item = create_estoque(db_session, EstoqueCreateSchema(nomeItem="  Papel   A4  "))
        assert item.nome_item == "Papel A4"

    def test_duplicado_com_espacos_levanta_erro(self, db_session: Session):
        db_session.add(Estoque(nome_item="Papel A4", quantidade_disponivel=1))
        db_session.commit()

        with pytest.raises(EstoqueAlreadyExistsError):
            create_estoque(db_session, EstoqueCreateSchema(nomeItem="  papel   a4  "))

    def test_relanca_integrity_error_nao_unico(self, db_session: Session, monkeypatch):
        def commit_falha():
            raise IntegrityError("INSERT", {}, Exception("NOT NULL constraint failed: estoque.nomeitem"))

        monkeypatch.setattr(db_session, "commit", commit_falha)

        with pytest.raises(IntegrityError):
            create_estoque(db_session, EstoqueCreateSchema(nomeItem="Sem nome"))


class TestUpdateEstoque:
    def test_normaliza_nome(self, db_session: Session, estoque_item: Estoque):
        result = update_estoque(
            db_session,
            estoque_item.id_item_estoque,
            EstoqueUpdateSchema(nomeItem="  Papel   A4 Premium  "),
        )
        assert result.nome_item == "Papel A4 Premium"

    def test_duplicado_com_espacos_levanta_erro(self, db_session: Session, estoque_item: Estoque):
        db_session.add(Estoque(nome_item="Caneta", quantidade_disponivel=1))
        db_session.commit()

        with pytest.raises(EstoqueAlreadyExistsError):
            update_estoque(
                db_session,
                estoque_item.id_item_estoque,
                EstoqueUpdateSchema(nomeItem="  caneta  "),
            )


class TestSearchEstoque:
    def test_normaliza_termo(self, db_session: Session, estoque_item: Estoque):
        results = search_estoque_by_name(db_session, "  teste   item  ")
        assert any(item.id_item_estoque == estoque_item.id_item_estoque for item in results)


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
