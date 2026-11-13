import math
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

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


def create_access_token(
    *,
    subject: str,
    cargo: int,
    primeiro_acesso: bool = False,
    expires_delta: timedelta | None = None,
    token_version: int | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {
        "sub": subject,
        "cargo": cargo,
        "primeiro_acesso": bool(primeiro_acesso),
        "iat": now,
        "jti": uuid4().hex,
        "exp": expire,
    }
    if token_version is not None:
        payload["ver"] = int(token_version)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_reset_token(*, email: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.reset_token_expire_minutes))
    payload = {
        "sub": email,
        "type": "password_reset",
        "iat": now,
        "jti": uuid4().hex,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def _decode_typed_token(token: str, expected_type: str) -> dict:
    settings = get_settings()
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "type", "exp"]},
    )
    exp = payload.get("exp")
    if (
        payload.get("type") != expected_type
        or not isinstance(payload.get("sub"), str)
        or not payload["sub"]
        or isinstance(exp, bool)
        or not isinstance(exp, (int, float))
        or (isinstance(exp, float) and not math.isfinite(exp))
        or exp <= time.time()
    ):
        raise jwt.PyJWTError("Invalid token type")
    return payload


def decode_reset_token(token: str) -> dict:
    return _decode_typed_token(token, "password_reset")


def create_first_access_token(*, email: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.first_access_token_expire_minutes)
    )
    payload = {
        "sub": email,
        "type": "first_access",
        "iat": now,
        "jti": uuid4().hex,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_first_access_token(token: str) -> dict:
    return _decode_typed_token(token, "first_access")