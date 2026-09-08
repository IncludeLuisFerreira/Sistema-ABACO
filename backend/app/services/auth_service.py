from jwt import PyJWTError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_reset_token, decode_reset_token, hash_password, verify_password
from app.models.usuario import Usuario


class InvalidCredentialsError(Exception):
    pass


class EmailNotFoundError(Exception):
    pass


class PasswordsDoNotMatchError(Exception):
    pass


class InvalidResetTokenError(Exception):
    pass


def authenticate_user(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario or not usuario.senha_hash:
        raise InvalidCredentialsError

    if not verify_password(senha, usuario.senha_hash):
        raise InvalidCredentialsError

    return usuario


def build_login_response(usuario: Usuario) -> dict:
    token = create_access_token(subject=str(usuario.id_usuario), cargo=int(usuario.cargo or 0))
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "idUsuario": usuario.id_usuario,
            "nome": usuario.nome,
            "email": usuario.email,
            "cargo": usuario.cargo,
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