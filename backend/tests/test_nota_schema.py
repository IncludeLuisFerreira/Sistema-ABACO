import pytest
from pydantic import ValidationError

from app.schemas.nota_schema import NotaBatchSchema, NotaItemSchema


class TestNotaItemSchema:
    @pytest.mark.parametrize("nota", [0, 10, 7.5])
    def test_nota_na_faixa_aceita(self, nota):
        item = NotaItemSchema(idMatricula=1, nota=nota)
        assert item.nota == float(nota)

    @pytest.mark.parametrize("nota", [-0.1, 10.1])
    def test_nota_fora_da_faixa_rejeitada(self, nota):
        with pytest.raises(ValidationError):
            NotaItemSchema(idMatricula=1, nota=nota)

    def test_nota_ausente_aceita(self):
        assert NotaItemSchema(idMatricula=1).nota is None

    @pytest.mark.parametrize("nota", [True, "7.5"])
    def test_nota_nao_numerica_rejeitada(self, nota):
        with pytest.raises(ValidationError):
            NotaItemSchema(idMatricula=1, nota=nota)


class TestNotaBatchSchema:
    def test_batch_valido(self):
        batch = NotaBatchSchema(
            idTurma=1,
            prova=1,
            notas=[NotaItemSchema(idMatricula=1, nota=7.5)],
        )
        assert batch.prova == 1

    @pytest.mark.parametrize("prova", [0, -1])
    def test_prova_menor_que_um_rejeitada(self, prova):
        with pytest.raises(ValidationError):
            NotaBatchSchema(idTurma=1, prova=prova, notas=[])

    @pytest.mark.parametrize("prova", [True, 1.0, "1"])
    def test_prova_nao_inteira_rejeitada(self, prova):
        with pytest.raises(ValidationError):
            NotaBatchSchema(idTurma=1, prova=prova, notas=[])
