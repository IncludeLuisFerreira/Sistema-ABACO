from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    # FIXME: except genérico mascara hash bcrypt corrompido como "senha incorreta"
    except Exception:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(*, subject: str, cargo: int, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    # TODO: JWT sem jti/iat; não há revogação de token nem logout real
    payload = {"sub": subject, "cargo": cargo, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_reset_token(*, email: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.reset_token_expire_minutes))
    payload = {"sub": email, "type": "password_reset", "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_reset_token(token: str) -> dict:
    settings = get_settings()
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    if payload.get("type") != "password_reset":
        raise jwt.PyJWTError("Invalid token type")
    return payload