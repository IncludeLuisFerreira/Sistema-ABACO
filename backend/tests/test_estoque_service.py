import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.estoque import Estoque
from app.schemas.estoque_schema import EstoqueCreateSchema, EstoqueUpdateSchema
from app.services import estoque_service
from app.services.estoque_service import (
    EstoqueAlreadyExistsError,
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


class TestIntegridadeEstoque:
    def test_create_integridade_nao_unica_propaga(self, db_session: Session, monkeypatch):
        def commit_que_falha():
            raise IntegrityError(
                "INSERT INTO estoque",
                {},
                Exception("NOT NULL constraint failed: estoque.nomeitem"),
            )

        monkeypatch.setattr(db_session, "commit", commit_que_falha)

        with pytest.raises(IntegrityError):
            estoque_service.create_estoque(
                db_session,
                EstoqueCreateSchema(nomeItem="Caneta", quantidadeDisponivel=1),
            )

    def test_create_integridade_unica_por_pgcode_vira_dominio(self, db_session: Session, monkeypatch):
        class OrigPostgres:
            pgcode = "23505"

        def commit_que_falha():
            raise IntegrityError("INSERT INTO estoque", {}, OrigPostgres())

        monkeypatch.setattr(db_session, "commit", commit_que_falha)

        with pytest.raises(EstoqueAlreadyExistsError):
            estoque_service.create_estoque(
                db_session,
                EstoqueCreateSchema(nomeItem="Caneta", quantidadeDisponivel=1),
            )

    def test_update_duplicado_mensagem_usa_nome_tentado(self, db_session: Session):
        db_session.add(Estoque(nome_item="Cola", quantidade_disponivel=1))
        db_session.add(Estoque(nome_item="Papel A4", quantidade_disponivel=1))
        db_session.commit()
        cola = db_session.query(Estoque).filter(Estoque.nome_item == "Cola").one()

        with pytest.raises(EstoqueAlreadyExistsError) as excinfo:
            estoque_service.update_estoque(
                db_session,
                cola.id_item_estoque,
                EstoqueUpdateSchema(nomeItem="  Papel   A4  "),
            )

        mensagem = str(excinfo.value)
        assert "Papel A4" in mensagem
        assert "'Cola'" not in mensagem

    def test_search_normaliza_espacos_do_termo(self, db_session: Session):
        db_session.add(Estoque(nome_item="Papel A4", quantidade_disponivel=1))
        db_session.commit()

        resultados = estoque_service.search_estoque_by_name(db_session, " papel   a4 ")

        assert [item.nome_item for item in resultados] == ["Papel A4"]
