from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.validators import normalize_email_institucional, normalize_nome, normalize_telefone_br


class UsuarioCreateSchema(BaseModel):
	nome: str = Field(min_length=1)
	email: EmailStr
	# FIXME: política de senha fraca (min_length=1) difere do reset (8+ com letra/número)
	senha: str = Field(min_length=1)
	cargo: int = Field(ge=1, le=3)
	telefone: str | None = None
	endereco: str | None = None

	@field_validator("email")
	@classmethod
	def validar_email(cls, value: str) -> str:
		return normalize_email_institucional(value)

	@field_validator("nome")
	@classmethod
	def validar_nome(cls, value: str) -> str:
		return normalize_nome(value)

	@field_validator("telefone")
	@classmethod
	def validar_telefone(cls, value: str | None) -> str | None:
		return normalize_telefone_br(value)


class UsuarioUpdateSchema(BaseModel):
	nome: str = Field(min_length=1)
	telefone: str | None = None
	endereco: str | None = None
	cargo: int = Field(ge=1, le=3)

	@field_validator("nome")
	@classmethod
	def validar_nome(cls, value: str) -> str:
		return normalize_nome(value)

	@field_validator("telefone")
	@classmethod
	def validar_telefone(cls, value: str | None) -> str | None:
		return normalize_telefone_br(value)


class UsuarioResponseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True, populate_by_name=True)

	id_usuario: int = Field(alias="idUsuario")
	nome: str | None = None
	telefone: str | None = None
	email: EmailStr | None = None
	cargo: int | None = None
	endereco: str | None = None
	primeiro_acesso: bool = False
