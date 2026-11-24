import hmac

from jwt import PyJWTError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_first_access_token,
    decode_reset_token,
    hash_password,
    password_version,
    verify_password,
)
from app.core.validators import normalize_email
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


def get_authenticated_user(db: Session, subject: str | None) -> Usuario:
    try:
        usuario_id = int(subject or "")
    except (TypeError, ValueError):
        raise InvalidCredentialsError

    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).populate_existing().first()
    if not usuario:
        raise InvalidCredentialsError
    return usuario


def authenticate_user(db: Session, email: str, senha: str) -> Usuario:
    normalized_email = normalize_email(email)
    usuario = db.query(Usuario).filter(func.lower(Usuario.email) == normalized_email).first()

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
        token_version=int(usuario.token_version or 0),
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


def revoke_user_sessions(db: Session, usuario_id: int) -> None:
    """Invalida todos os access tokens emitidos para o usuario."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    if not usuario:
        return
    usuario.token_version = int(usuario.token_version or 0) + 1
    db.commit()


def process_forgot_password(db: Session, email: str) -> tuple[Usuario, str]:
    normalized_email = normalize_email(email)
    usuario = db.query(Usuario).filter(func.lower(Usuario.email) == normalized_email).first()
    if not usuario:
        raise EmailNotFoundError

    token = create_reset_token(email=usuario.email, password_hash=usuario.senha_hash)
    return usuario, token


def _consume_password_token(db: Session, payload: dict, nova_senha: str, *, first_access: bool = False) -> bool:
    usuario = db.query(Usuario).filter(Usuario.email == payload.get("sub")).populate_existing().first()
    version = payload.get("password_version")
    if (
        not usuario
        or not isinstance(version, str)
        or not hmac.compare_digest(version.encode("utf-8"), password_version(usuario.senha_hash).encode("utf-8"))
        or (first_access and not usuario.primeiro_acesso)
    ):
        return False

    # A condição na atualização garante consumo único mesmo em requests simultâneos.
    updated = db.query(Usuario).filter(
        Usuario.id_usuario == usuario.id_usuario,
        Usuario.senha_hash == usuario.senha_hash,
    ).update(
        {
            Usuario.senha_hash: hash_password(nova_senha),
            Usuario.primeiro_acesso: False,
            # Consumir o link tambem revoga as sessoes emitidas antes da troca.
            Usuario.token_version: int(usuario.token_version or 0) + 1,
        },
        synchronize_session=False,
    )
    if updated != 1:
        db.rollback()
        return False
    db.commit()
    return True


def process_reset_password(db: Session, token: str, nova_senha: str, confirmar_senha: str) -> None:
    if nova_senha != confirmar_senha:
        raise PasswordsDoNotMatchError

    try:
        payload = decode_reset_token(token)
    except PyJWTError:
        raise InvalidResetTokenError

    if not _consume_password_token(db, payload, nova_senha):
        raise InvalidResetTokenError


def process_first_access_password(db: Session, token: str, nova_senha: str, confirmar_senha: str) -> None:
    if nova_senha != confirmar_senha:
        raise PasswordsDoNotMatchError

    try:
        payload = decode_first_access_token(token)
    except PyJWTError:
        raise InvalidFirstAccessTokenError

    if not _consume_password_token(db, payload, nova_senha, first_access=True):
        raise InvalidFirstAccessTokenError


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
    usuario.token_version = int(usuario.token_version or 0) + 1
    db.commit()
    db.refresh(usuario)
    return usuario
