import pytest
from pydantic import ValidationError

from app.schemas.estoque_schema import EstoqueBaixaSchema, EstoqueCreateSchema, EstoqueUpdateSchema


class TestEstoqueBaixaSchema:
    def test_valid_payload(self):
        schema = EstoqueBaixaSchema(quantidade=5, justificativa="Consumo em aula")
        assert schema.quantidade == 5
        assert schema.justificativa == "Consumo em aula"

    def test_quantidade_zero_rejected(self):
        with pytest.raises(ValidationError) as exc:
            EstoqueBaixaSchema(quantidade=0, justificativa="Teste")
        assert "quantidade" in str(exc.value).lower()

    def test_quantidade_negativa_rejected(self):
        with pytest.raises(ValidationError) as exc:
            EstoqueBaixaSchema(quantidade=-1, justificativa="Teste")
        assert "quantidade" in str(exc.value).lower()

    def test_justificativa_vazia_rejected(self):
        with pytest.raises(ValidationError):
            EstoqueBaixaSchema(quantidade=1, justificativa="")

    def test_quantidade_gt_zero_valid(self):
        schema = EstoqueBaixaSchema(quantidade=1, justificativa="Teste")
        assert schema.quantidade == 1


class TestEstoqueCreateSchema:
    def test_quantidades_zero_aceitas(self):
        schema = EstoqueCreateSchema(
            nomeItem="Caneta",
            quantidadeDisponivel=0,
            estoqueMinimo=0,
        )
        assert schema.quantidadeDisponivel == 0
        assert schema.estoqueMinimo == 0

    def test_negative_quantidade_disponivel_rejected(self):
        with pytest.raises(ValidationError):
            EstoqueCreateSchema(nomeItem="Item", quantidadeDisponivel=-5)

    def test_negative_estoque_minimo_rejected(self):
        with pytest.raises(ValidationError):
            EstoqueCreateSchema(nomeItem="Item", estoqueMinimo=-5)

    def test_nome_item_normalizado(self):
        schema = EstoqueCreateSchema(nomeItem="  Caneta  ")
        assert schema.nomeItem == "Caneta"

    def test_nome_item_em_branco_rejeitado(self):
        with pytest.raises(ValidationError):
            EstoqueCreateSchema(nomeItem="   ")

    @pytest.mark.parametrize("valor", [True, 1.0, "1"])
    def test_quantidade_nao_inteira_rejeitada(self, valor):
        with pytest.raises(ValidationError):
            EstoqueCreateSchema(nomeItem="Item", quantidadeDisponivel=valor)


class TestEstoqueUpdateSchema:
    def test_quantidades_zero_aceitas(self):
        schema = EstoqueUpdateSchema(quantidadeDisponivel=0, estoqueMinimo=0)
        assert schema.quantidadeDisponivel == 0
        assert schema.estoqueMinimo == 0

    def test_negative_quantidade_disponivel_rejected(self):
        with pytest.raises(ValidationError):
            EstoqueUpdateSchema(quantidadeDisponivel=-1)

    def test_negative_estoque_minimo_rejected(self):
        with pytest.raises(ValidationError):
            EstoqueUpdateSchema(estoqueMinimo=-5)

    def test_nome_item_normalizado(self):
        schema = EstoqueUpdateSchema(nomeItem="  Caneta  ")
        assert schema.nomeItem == "Caneta"

    def test_nome_item_em_branco_rejeitado(self):
        with pytest.raises(ValidationError):
            EstoqueUpdateSchema(nomeItem="   ")

    @pytest.mark.parametrize("valor", [True, 1.0, "1"])
    def test_quantidade_nao_inteira_rejeitada(self, valor):
        with pytest.raises(ValidationError):
            EstoqueUpdateSchema(quantidadeDisponivel=valor)
