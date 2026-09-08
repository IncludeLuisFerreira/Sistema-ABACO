from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreateSchema(BaseModel):
	nome: str = Field(min_length=1)
	email: EmailStr
	senha: str = Field(min_length=1)
	cargo: int = Field(ge=1, le=3)
	telefone: str | None = None


class UsuarioUpdateSchema(BaseModel):
	nome: str = Field(min_length=1)
	telefone: str | None = None
	cargo: int = Field(ge=1, le=3)


class UsuarioResponseSchema(BaseModel):
	model_config = ConfigDict(from_attributes=True, populate_by_name=True)

	id_usuario: int = Field(alias="idUsuario")
	nome: str | None = None
	telefone: str | None = None
	email: EmailStr | None = None
	cargo: int | None = None