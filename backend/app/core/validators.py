import re

# Celular BR: DDD (2 dígitos, sem zero à esquerda) + 9 dígitos = 11 no total.
TELEFONE_BR_DIGITS = re.compile(r"^[1-9]\d{10}$")
TELEFONE_BR_MSG = "Telefone deve conter DDD + 9 dígitos (ex: 11999999999)"

# Nome: letras (com acento), espaços, hífen e apóstrofo; mínimo 3 caracteres.
NOME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿĀ-ž' -]+$")
NOME_MIN_LENGTH = 3
NOME_MSG = "Nome deve ter ao menos 3 letras e conter apenas letras, espaços, hífen ou apóstrofo"

ALLOWED_EMAIL_DOMAINS = ("abaco.org.br",)
EMAIL_DOMAIN_MSG = "E-mail deve ser do domínio @abaco.org.br"


def normalize_telefone_br(value: str | None) -> str | None:
	"""Aceita vazio/None; rejeita formato inválido; devolve só dígitos."""
	if value is None:
		return None

	digits = re.sub(r"\D", "", value.strip())
	if not digits:
		return None

	if not TELEFONE_BR_DIGITS.fullmatch(digits):
		raise ValueError(TELEFONE_BR_MSG)

	return digits


def normalize_nome(value: str) -> str:
	cleaned = re.sub(r"\s+", " ", value.strip())
	if len(cleaned) < NOME_MIN_LENGTH or not NOME_PATTERN.fullmatch(cleaned):
		raise ValueError(NOME_MSG)
	return cleaned


def normalize_email_institucional(value: str) -> str:
	email = value.strip().lower()
	domain = email.rsplit("@", 1)[-1]
	if domain not in ALLOWED_EMAIL_DOMAINS:
		raise ValueError(EMAIL_DOMAIN_MSG)
	return email
