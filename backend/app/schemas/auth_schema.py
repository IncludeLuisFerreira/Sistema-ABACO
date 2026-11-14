import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.validators import normalize_email


SENHA_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


class LoginRequest(BaseModel):
	email: EmailStr
	senha: str = Field(min_length=1)

	@field_validator("email", mode="before")
	@classmethod
	def clean_email(cls, value: object) -> object:
		if isinstance(value, str):
			return normalize_email(value)
		return value


class ForgotPasswordRequest(BaseModel):
	email: EmailStr

	@field_validator("email", mode="before")
	@classmethod
	def clean_email(cls, value: object) -> object:
		if isinstance(value, str):
			return normalize_email(value)
		return value
    

class PasswordPairRequest(BaseModel):
    nova_senha: str = Field(min_length=8)
    confirmar_senha: str = Field(min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não conferem")
        if not SENHA_PATTERN.match(self.nova_senha):
            raise ValueError("A senha deve conter pelo menos uma letra e um número")
        return self


class ResetPasswordRequest(PasswordPairRequest):
    token: str = Field(min_length=1)


class FirstAccessPasswordRequest(PasswordPairRequest):
    token: str = Field(min_length=1)


class ChangePasswordRequest(PasswordPairRequest):
    senha_atual: str = Field(min_length=1)


class UsuarioResponse(BaseModel):
    idUsuario: int
    nome: str | None
    email: EmailStr
    cargo: int | None
    primeiro_acesso: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class MessageResponse(BaseModel):
    message: str