import pytest
from pydantic import ValidationError

from app.schemas.estoque_schema import EstoqueBaixaSchema, EstoqueCreateSchema


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
    def test_negative_quantidade_disponivel_allowed(self):
        schema = EstoqueCreateSchema(nomeItem="Item", quantidadeDisponivel=-5)
        assert schema.quantidadeDisponivel == -5

    def test_negative_estoque_minimo_allowed(self):
        schema = EstoqueCreateSchema(nomeItem="Item", estoqueMinimo=-5)
        assert schema.estoqueMinimo == -5
