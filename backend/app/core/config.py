from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
INSECURE_DEFAULT_SECRET = "development_secret_change_me"
PRODUCTION_ENVIRONMENTS = {"production", "prod"}


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

	app_name: str = "SGA ABACO API"
	environment: str = Field(
		default="development",
		validation_alias=AliasChoices("APP_ENV", "ENVIRONMENT"),
	)
	# FIXME: credenciais de banco hardcoded no default (postgres:postgres)
	database_url: str = Field(default="postgresql+psycopg2://postgres:postgres@database:5432/sga_abacos", alias="DATABASE_URL")
	admin_seed_email: str | None = Field(default=None, alias="ADMIN_SEED_EMAIL")
	admin_seed_password: str | None = Field(default=None, alias="ADMIN_SEED_PASSWORD")
	# O default inseguro só é aceito fora de produção; ver _require_strong_secret_in_production.
	secret_key: str = Field(
		default=INSECURE_DEFAULT_SECRET,
		validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
	)
	jwt_algorithm: str = "HS256"
	access_token_expire_minutes: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
	reset_token_expire_minutes: int = Field(default=30, alias="RESET_TOKEN_EXPIRE_MINUTES")
	first_access_token_expire_minutes: int = Field(default=1440, alias="FIRST_ACCESS_TOKEN_EXPIRE_MINUTES")
	session_cookie_secure: bool | None = Field(default=None, alias="SESSION_COOKIE_SECURE")
	session_cookie_samesite: str = Field(default="lax", alias="SESSION_COOKIE_SAMESITE")
	smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
	smtp_port: int = Field(default=587, alias="SMTP_PORT")
	smtp_user: str = Field(default="", alias="SMTP_USER")
	smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
	smtp_from: str = Field(default="noreply@abaco.org.br", alias="SMTP_FROM")
	smtp_timeout_seconds: int = Field(default=15, alias="SMTP_TIMEOUT_SECONDS")
	email_sender_name: str = Field(default="SGA ABACO", alias="EMAIL_SENDER_NAME")
	brevo_api_key: str = Field(
		default="",
		validation_alias=AliasChoices("BREVO_API_KEY", "SENDINBLUE_API_KEY"),
	)
	frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
	cors_origins: str = Field(
		default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://localhost:8000",
		alias="CORS_ORIGINS",
	)
	rate_limit_auth: str = Field(default="5/minute", alias="RATE_LIMIT_AUTH")
	rate_limit_default: str = Field(default="60/minute", alias="RATE_LIMIT_DEFAULT")

	@field_validator("smtp_from", mode="before")
	@classmethod
	def _fallback_smtp_from_when_blank(cls, value: str | None) -> str:
		if value is None or not str(value).strip():
			return "noreply@abaco.org.br"
		return str(value).strip()

	@model_validator(mode="after")
	def _require_strong_secret_in_production(self) -> "Settings":
		if self.is_production:
			secret = (self.secret_key or "").strip()
			if not secret or secret == INSECURE_DEFAULT_SECRET:
				raise ValueError(
					"SECRET_KEY/JWT_SECRET deve ser definido com um valor proprio em producao"
				)
			if len(secret) < 32:
				raise ValueError(
					"SECRET_KEY/JWT_SECRET deve ter pelo menos 32 caracteres em producao"
				)
		return self

	@property
	def is_production(self) -> bool:
		return self.environment.strip().lower() in PRODUCTION_ENVIRONMENTS

	@property
	def effective_session_cookie_secure(self) -> bool:
		if self.session_cookie_secure is None:
			return self.is_production
		return self.session_cookie_secure

	@property
	def cors_origin_list(self) -> list[str]:
		return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()
