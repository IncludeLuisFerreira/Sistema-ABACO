from fastapi import Depends, Header, HTTPException, status
import jwt

from app.core.config import get_settings


AUTH_ERROR_HEADERS = {"WWW-Authenticate": "Bearer"}


def _extract_token(authorization: str | None) -> str:
	if not authorization:
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
		return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
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


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
	return decode_access_token(_extract_token(authorization))

def verify_cargo(*allowed_cargos: int):
	def dependency(authorization: str | None = Header(default=None)) -> dict:
		token = _extract_token(authorization)
		payload = decode_access_token(token)
		cargo = int(payload.get("cargo", 0) or 0)
		if cargo not in allowed_cargos:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Acesso negado. Você não tem permissão para acessar este recurso.",
			)
		return payload

	return dependency


verify_director_role = verify_cargo(1)
