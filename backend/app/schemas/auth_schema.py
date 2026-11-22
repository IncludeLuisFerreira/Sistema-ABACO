import re
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, EmailStr, Field, model_validator

from app.core.validators import normalize_email


SENHA_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


def _normalize_email_input(value: object) -> object:
    if isinstance(value, str):
        return normalize_email(value)
    return value


NormalizedEmail = Annotated[EmailStr, BeforeValidator(_normalize_email_input)]


class LoginRequest(BaseModel):
    email: NormalizedEmail
    senha: str = Field(min_length=1)


class ForgotPasswordRequest(BaseModel):
    email: NormalizedEmail


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