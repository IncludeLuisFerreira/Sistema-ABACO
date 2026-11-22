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

	@pytest.mark.parametrize(
		"email",
		["pessoa@gmail.com", "pessoa@abaco.org.br", "fulano@empresa.com.br", "alguem@outlook.com"],
	)
	def test_email_de_qualquer_dominio_aceito(self, email):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email=email,
			senha="senha123",
			cargo=2,
		)
		assert payload.email == email

	def test_email_gmail_normalizado_para_minusculo(self):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email="Novo.Usuario@GMAIL.com",
			senha="senha123",
			cargo=2,
		)
		assert payload.email == "novo.usuario@gmail.com"

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

	@pytest.mark.parametrize("senha", ["1234567", "somenteletras", "12345678"])
	def test_senha_fraca_rejeitada(self, senha):
		with pytest.raises(ValidationError):
			UsuarioCreateSchema(
				nome="Novo Usuario",
				email="novo@abaco.org.br",
				senha=senha,
				cargo=2,
			)

	def test_senha_com_letra_e_numero_aceita(self):
		payload = UsuarioCreateSchema(
			nome="Novo Usuario",
			email="novo@abaco.org.br",
			senha="senha123",
			cargo=2,
		)
		assert payload.senha == "senha123"


@pytest.mark.parametrize("nome", ["---", "a--", "a b"])
def test_nome_exige_tres_letras(nome):
    with pytest.raises(ValidationError):
        UsuarioCreateSchema(nome=nome, email="novo@abaco.org.br", senha="senha123", cargo=2)
