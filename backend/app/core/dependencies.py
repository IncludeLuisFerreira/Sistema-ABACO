from fastapi import Depends, Header, HTTPException, status
import jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.database import get_db
from app.services.auth_service import InvalidCredentialsError, get_authenticated_user


AUTH_ERROR_HEADERS = {"WWW-Authenticate": "Bearer"}


def _extract_token(authorization: str | None) -> str:
	if not authorization:
		# FIXME: 401 sem header WWW-Authenticate (inconsistente com o restante)
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token de acesso não fornecido. Faça login para continuar.",
		)

	parts = authorization.split()
	if len(parts) == 2 and parts[0].lower() == "bearer":
		return parts[1]

	raise HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Formato de token inválido",
		headers=AUTH_ERROR_HEADERS,
	)


def decode_access_token(token: str) -> dict:
	settings = get_settings()
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
	except jwt.ExpiredSignatureError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token expirado",
			headers=AUTH_ERROR_HEADERS,
		)
	except jwt.PyJWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token de acesso inválido ou expirado. Faça login novamente.",
		) from exc

	if payload.get("type") not in (None, "access"):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token de acesso inválido ou expirado. Faça login novamente.",
			headers=AUTH_ERROR_HEADERS,
		)

	return payload


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
	payload = decode_access_token(_extract_token(authorization))
	try:
		usuario = get_authenticated_user(db, payload.get("sub"))
	except InvalidCredentialsError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Usuário não encontrado. Faça login novamente.",
			headers=AUTH_ERROR_HEADERS,
		) from exc
	payload["cargo"] = int(usuario.cargo or 0)
	payload["primeiro_acesso"] = bool(usuario.primeiro_acesso)
	return payload

def verify_cargo(*allowed_cargos: int):
	def dependency(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict:
		payload = get_current_user(authorization, db)
		cargo = int(payload.get("cargo", 0) or 0)
		if cargo not in allowed_cargos:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Acesso negado. Você não tem permissão para acessar este recurso.",
			)
		return payload

	return dependency
