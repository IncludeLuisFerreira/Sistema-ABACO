from jwt import PyJWTError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_first_access_token,
    decode_reset_token,
    hash_password,
    verify_password,
)
from app.models.usuario import Usuario


class InvalidCredentialsError(Exception):
    pass


class EmailNotFoundError(Exception):
    pass


class PasswordsDoNotMatchError(Exception):
    pass


class InvalidResetTokenError(Exception):
    pass


class InvalidFirstAccessTokenError(Exception):
    pass


class InvalidCurrentPasswordError(Exception):
    pass


def authenticate_user(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not usuario.senha_hash:
        raise InvalidCredentialsError

    if not verify_password(senha, usuario.senha_hash):
        raise InvalidCredentialsError

    return usuario


def build_login_response(usuario: Usuario) -> dict:
    primeiro_acesso = bool(usuario.primeiro_acesso)
    token = create_access_token(
        subject=str(usuario.id_usuario),
        cargo=int(usuario.cargo or 0),
        primeiro_acesso=primeiro_acesso,
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "idUsuario": usuario.id_usuario,
            "nome": usuario.nome,
            "email": usuario.email,
            "cargo": usuario.cargo,
            "primeiro_acesso": primeiro_acesso,
        },
    }


def process_forgot_password(db: Session, email: str) -> str:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise EmailNotFoundError

    token = create_reset_token(email=email)
    return token


def process_reset_password(db: Session, token: str, nova_senha: str, confirmar_senha: str) -> None:
    if nova_senha != confirmar_senha:
        raise PasswordsDoNotMatchError

    try:
        payload = decode_reset_token(token)
    except PyJWTError:
        raise InvalidResetTokenError

    email = payload.get("sub")
    if not email:
        raise InvalidResetTokenError

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise InvalidResetTokenError

    usuario.senha_hash = hash_password(nova_senha)
    db.commit()


def process_first_access_password(db: Session, token: str, nova_senha: str, confirmar_senha: str) -> None:
    if nova_senha != confirmar_senha:
        raise PasswordsDoNotMatchError

    try:
        payload = decode_first_access_token(token)
    except PyJWTError:
        raise InvalidFirstAccessTokenError

    email = payload.get("sub")
    if not email:
        raise InvalidFirstAccessTokenError

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise InvalidFirstAccessTokenError

    usuario.senha_hash = hash_password(nova_senha)
    usuario.primeiro_acesso = False
    db.commit()


def change_password(
    db: Session, usuario_id: int, senha_atual: str, nova_senha: str, confirmar_senha: str
) -> Usuario:
    if nova_senha != confirmar_senha:
        raise PasswordsDoNotMatchError

    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario or not usuario.senha_hash:
        raise InvalidCurrentPasswordError

    if not verify_password(senha_atual, usuario.senha_hash):
        raise InvalidCurrentPasswordError

    usuario.senha_hash = hash_password(nova_senha)
    usuario.primeiro_acesso = False
    db.commit()
    db.refresh(usuario)
    return usuario