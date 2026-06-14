"""
EPM — Application Settings.
Loaded from environment variables (or .env.v2 file via docker-compose env_file).
All secrets MUST be provided at runtime — no defaults for sensitive values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.v2", extra="ignore")

    # ── Database ────────────────────────────────────────────────────────────────
    # asyncpg requires postgresql+asyncpg:// scheme
    # Example: postgresql+asyncpg://openagile:password@openagile_postgres/estate_portfolio
    DATABASE_URL: str

    # ── JWT ─────────────────────────────────────────────────────────────────────
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7

    # ── CORS ────────────────────────────────────────────────────────────────────
    # Comma-separated allowed origins for CORS middleware.
    # In production: https://demo.estate.zubbystudio.shop
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ── App ──────────────────────────────────────────────────────────────────────
    APP_ENV: str = "production"  # "development" | "production"

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"


settings = Settings()
