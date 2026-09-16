from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

	app_name: str = "SGA ABACO API"
	# FIXME: credenciais de banco hardcoded no default (postgres:postgres)
	database_url: str = Field(default="postgresql+psycopg2://postgres:postgres@database:5432/sga_abacos", alias="DATABASE_URL")
	admin_seed_email: str | None = Field(default=None, alias="ADMIN_SEED_EMAIL")
	admin_seed_password: str | None = Field(default=None, alias="ADMIN_SEED_PASSWORD")
	# FIXME: SECRET_KEY default insegura permite forjar tokens JWT se não definida
	secret_key: str = Field(
		default="development_secret_change_me",
		validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
	)
	jwt_algorithm: str = "HS256"
	access_token_expire_minutes: int = Field(default=120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
	reset_token_expire_minutes: int = Field(default=15, alias="RESET_TOKEN_EXPIRE_MINUTES")
	smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
	smtp_port: int = Field(default=587, alias="SMTP_PORT")
	smtp_user: str = Field(default="", alias="SMTP_USER")
	smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
	smtp_from: str = Field(default="noreply@abaco.org.br", alias="SMTP_FROM")
	frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
	cors_origins: str = Field(
		default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://localhost:8000",
		alias="CORS_ORIGINS",
	)
	rate_limit_auth: str = Field(default="5/minute", alias="RATE_LIMIT_AUTH")
	rate_limit_default: str = Field(default="60/minute", alias="RATE_LIMIT_DEFAULT")

	@property
	def cors_origin_list(self) -> list[str]:
		return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings()
