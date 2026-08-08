from functools import lru_cache
from pathlib import Path
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Centralized application configuration.

    Values are loaded from environment variables / a .env file.
    This is the single source of truth for config across the app —
    no module should call os.getenv() directly.
    """

    # ---- Project Metadata ----
    PROJECT_NAME: str = "NipunHire AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = Field(default=False, validation_alias="NIPUNHIRE_DEBUG")

    # ---- Database & Search ----
    MONGODB_URI: str
    DATABASE_NAME: str
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # ---- Auth & Encryption ----
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FIELD_ENCRYPTION_KEY: SecretStr = Field(default=SecretStr("pY27QGg6w3xL5v0kR7nB8m9kQ1wE2rT3yU4iO5pA6sD="))

    # ---- AI ----
    GEMINI_API_KEY: SecretStr = Field(default=SecretStr("your_gemini_api_key_here"))
    OPENAI_API_KEY: SecretStr = Field(default=SecretStr("your_openai_api_key_here"))
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_REQUEST_TIMEOUT_SECONDS: float = 30.0
    OPENAI_MAX_RETRIES: int = 3

    # ---- Vector Search ----
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_INDEX_DIR: Path = BACKEND_DIR / "uploads" / "vector_index"

    # ---- CORS (comma-separated in .env, parsed to list) ----
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()
