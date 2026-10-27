import pytest
from pydantic import ValidationError

from app.schemas.usuario_schema import UsuarioCreateSchema, UsuarioUpdateSchema


class TestUsuarioCreateSchemaValidation:
	def test_email_invalido_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioCreateSchema(
				nome="Novo Usuario",
				email="nao-eh-email",
				senha="senha123",
				cargo=2,
			)

	def test_email_dominio_externo_rejeitado(self):
		with pytest.raises(ValidationError) as exc:
			UsuarioCreateSchema(
				nome="Novo Usuario",
				email="pessoa@gmail.com",
				senha="senha123",
				cargo=2,
			)
		assert "abaco.org.br" in str(exc.value)

	def test_email_normalizado_para_minusculo(self):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email="Novo.Usuario@Abaco.ORG.BR",
			senha="senha123",
			cargo=2,
		)
		assert payload.email == "novo.usuario@abaco.org.br"

	def test_nome_curto_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioCreateSchema(
				nome="Al",
				email="novo@abaco.org.br",
				senha="senha123",
				cargo=2,
			)

	def test_nome_com_numero_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioCreateSchema(
				nome="Ana 2",
				email="novo@abaco.org.br",
				senha="senha123",
				cargo=2,
			)

	def test_nome_normalizado(self):
		payload = UsuarioCreateSchema(
			nome="  Maria   Clara  ",
			email="maria.clara@abaco.org.br",
			senha="senha123",
			cargo=2,
		)
		assert payload.nome == "Maria Clara"

	def test_telefone_vazio_vira_none(self):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email="novo@abaco.org.br",
			senha="senha123",
			cargo=2,
			telefone="   ",
		)
		assert payload.telefone is None

	def test_telefone_formatado_normalizado(self):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email="novo@abaco.org.br",
			senha="senha123",
			cargo=2,
			telefone="(11) 99999-9999",
		)
		assert payload.telefone == "11999999999"

	def test_telefone_com_menos_de_11_digitos_rejeitado(self):
		with pytest.raises(ValidationError) as exc:
			UsuarioCreateSchema(
				nome="Novo Usuario",
				email="novo@abaco.org.br",
				senha="senha123",
				cargo=2,
				telefone="1199999999",
			)
		assert "DDD" in str(exc.value)

	def test_telefone_com_ddd_iniciando_em_zero_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioCreateSchema(
				nome="Novo Usuario",
				email="novo@abaco.org.br",
				senha="senha123",
				cargo=2,
				telefone="01999999999",
			)


class TestUsuarioUpdateSchemaValidation:
	def test_telefone_invalido_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioUpdateSchema(nome="Usuario", telefone="123", cargo=2)

	def test_telefone_valido_aceito(self):
		payload = UsuarioUpdateSchema(nome="Usuario", telefone="21987654321", cargo=2)
		assert payload.telefone == "21987654321"

	def test_nome_invalido_rejeitado(self):
		with pytest.raises(ValidationError):
			UsuarioUpdateSchema(nome="<>", telefone=None, cargo=2)
