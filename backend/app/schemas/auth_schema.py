import re

from pydantic import BaseModel, EmailStr, Field, model_validator


SENHA_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    nova_senha: str = Field(min_length=8)
    confirmar_senha: str = Field(min_length=8)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.nova_senha != self.confirmar_senha:
            raise ValueError("As senhas não conferem")
        if not SENHA_PATTERN.match(self.nova_senha):
            raise ValueError("A senha deve conter pelo menos uma letra e um número")
        return self


class UsuarioResponse(BaseModel):
    idUsuario: int
    nome: str | None
    email: EmailStr
    cargo: int | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class MessageResponse(BaseModel):
    message: str