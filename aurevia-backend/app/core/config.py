"""
Centralized app configuration.
Loads from environment variables / .env file so secrets never live in code.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "Aurevia"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./aurevia.db"

    # Auth
    secret_key: str = "insecure-dev-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI Service
    ai_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"
    ai_api_url: str = "https://api.anthropic.com/v1/messages"
    ai_request_timeout_seconds: int = 30

    # CORS - comma separated string, parsed into a list.
    # Add your exact deployed frontend URL(s) here, e.g.:
    # CORS_ORIGINS=https://aurevia.vercel.app,http://localhost:3000,http://localhost:5173
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Optional regex to also allow Vercel preview deployments, which get a
    # unique URL per branch/PR (e.g. aurevia-git-feature-x-yourteam.vercel.app).
    # Leave blank to disable and rely on the exact-match list above only.
    # Example: r"https://aurevia-.*\.vercel\.app"
    cors_origin_regex: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # cached so we don't re-read env vars on every request
    return Settings()


settings = get_settings()
