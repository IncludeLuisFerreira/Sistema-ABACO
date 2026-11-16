import pytest
from pydantic import ValidationError

from app.schemas.estoque_schema import EstoqueCreateSchema, EstoqueUpdateSchema
from app.schemas.matricula_schema import MatriculaCreateSchema, MatriculaUpdateSchema
from app.schemas.nota_schema import NotaBatchSchema, NotaItemSchema


class TestEstoqueSchemaValidation:
	def test_quantidades_nao_negativas_no_create(self):
		payload = EstoqueCreateSchema(
			nomeItem="Caneta",
			quantidadeDisponivel=0,
			estoqueMinimo=0,
		)
		assert payload.quantidadeDisponivel == 0
		assert payload.estoqueMinimo == 0

	def test_quantidade_disponivel_negativa_rejeitada_no_create(self):
		with pytest.raises(ValidationError):
			EstoqueCreateSchema(nomeItem="Caneta", quantidadeDisponivel=-1)

	def test_estoque_minimo_negativo_rejeitado_no_create(self):
		with pytest.raises(ValidationError):
			EstoqueCreateSchema(nomeItem="Caneta", estoqueMinimo=-1)

	def test_quantidade_disponivel_negativa_rejeitada_no_update(self):
		with pytest.raises(ValidationError):
			EstoqueUpdateSchema(quantidadeDisponivel=-1)

	def test_estoque_minimo_negativo_rejeitado_no_update(self):
		with pytest.raises(ValidationError):
			EstoqueUpdateSchema(estoqueMinimo=-5)


class TestNotaSchemaValidation:
	def test_nota_na_faixa_aceita(self):
		item = NotaItemSchema(idMatricula=1, nota=7.5)
		batch = NotaBatchSchema(idTurma=1, prova=1, notas=[item])
		assert batch.prova == 1
		assert batch.notas[0].nota == 7.5

	def test_nota_fora_da_faixa_rejeitada(self):
		with pytest.raises(ValidationError):
			NotaItemSchema(idMatricula=1, nota=-0.1)
		with pytest.raises(ValidationError):
			NotaItemSchema(idMatricula=1, nota=10.1)

	def test_prova_menor_que_um_rejeitada(self):
		with pytest.raises(ValidationError):
			NotaBatchSchema(idTurma=1, prova=0, notas=[])


class TestMatriculaStatusSchemaValidation:
	def test_status_validos_aceitados(self):
		assert MatriculaCreateSchema(idAluno=1, idTurma=1, status=0).status == 0
		assert MatriculaCreateSchema(idAluno=1, idTurma=1, status=1).status == 1
		assert MatriculaUpdateSchema(status=2).status == 2

	def test_status_invalido_rejeitado(self):
		with pytest.raises(ValidationError):
			MatriculaCreateSchema(idAluno=1, idTurma=1, status=3)
		with pytest.raises(ValidationError):
			MatriculaUpdateSchema(status=-1)
