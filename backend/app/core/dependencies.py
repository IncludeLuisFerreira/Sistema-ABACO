from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
import jwt

from app.core.config import get_settings
from app.core.session import (
	CSRF_COOKIE_NAME,
	CSRF_HEADER_NAME,
	SAFE_METHODS,
	SESSION_COOKIE_NAME,
	csrf_tokens_match,
)
from app.db.database import get_db
from app.models.usuario import Usuario


AUTH_ERROR_HEADERS = {"WWW-Authenticate": "Bearer"}
INVALID_TOKEN_DETAIL = "Token de acesso inválido ou expirado. Faça login novamente."


def _unauthorized(detail: str, *, with_headers: bool = True) -> HTTPException:
	return HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail=detail,
		headers=AUTH_ERROR_HEADERS if with_headers else None,
	)


def _extract_token(request: Request, authorization: str | None) -> tuple[str, str]:
	if authorization:
		parts = authorization.split()
		if len(parts) == 2 and parts[0].lower() == "bearer":
			return "header", parts[1]
		raise _unauthorized("Formato de token inválido")

	cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
	if cookie_token:
		return "cookie", cookie_token

	raise _unauthorized("Token de acesso não fornecido. Faça login para continuar.", with_headers=False)


def _enforce_csrf(request: Request) -> None:
	if request.method.upper() in SAFE_METHODS:
		return

	cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
	header_token = request.headers.get(CSRF_HEADER_NAME)
	if not csrf_tokens_match(cookie_token, header_token):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Requisição bloqueada: token CSRF inválido ou ausente.",
		)


def _validate_revocable_token(payload: dict, db: Session) -> None:
	"""Valida versao/cargo no banco apenas para tokens emitidos com o claim `ver`.

	Tokens legados (sem `ver`) continuam validos ate expirar; apos esse periodo todo
	token novo passa pela checagem de revogacao.
	"""
	if "ver" not in payload:
		return

	try:
		usuario_id = int(payload.get("sub", ""))
		token_version = int(payload.get("ver"))
		cargo = int(payload.get("cargo", 0) or 0)
	except (TypeError, ValueError) as exc:
		raise _unauthorized(INVALID_TOKEN_DETAIL) from exc

	usuario = db.get(Usuario, usuario_id) if db is not None else None
	if (
		usuario is None
		or int(usuario.token_version or 0) != token_version
		or int(usuario.cargo or 0) != cargo
	):
		raise _unauthorized(INVALID_TOKEN_DETAIL)


def decode_access_token(token: str) -> dict:
	settings = get_settings()
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
	except jwt.ExpiredSignatureError:
		raise _unauthorized("Token expirado")
	except jwt.PyJWTError as exc:
		raise _unauthorized(INVALID_TOKEN_DETAIL) from exc

	if payload.get("type") not in (None, "access"):
		raise _unauthorized(INVALID_TOKEN_DETAIL)

	return payload


def _resolve_current_user(request: Request, authorization: str | None, db: Session) -> dict:
	source, token = _extract_token(request, authorization)
	payload = decode_access_token(token)
	if source == "cookie":
		_enforce_csrf(request)
	_validate_revocable_token(payload, db)
	return payload


def get_current_user(
	request: Request,
	authorization: str | None = Header(default=None),
	db: Session = Depends(get_db),
) -> dict:
	return _resolve_current_user(request, authorization, db)


def verify_cargo(*allowed_cargos: int):
	def dependency(
		request: Request,
		authorization: str | None = Header(default=None),
		db: Session = Depends(get_db),
	) -> dict:
		payload = _resolve_current_user(request, authorization, db)
		cargo = int(payload.get("cargo", 0) or 0)
		if cargo not in allowed_cargos:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Acesso negado. Você não tem permissão para acessar este recurso.",
			)
		return payload

	return dependency
