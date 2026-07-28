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
    PROJECT_NAME: str = "HireSense AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    # Avoid the generic DEBUG variable, which is commonly set by tooling to
    # non-boolean values (for example, "release").
    DEBUG: bool = Field(default=False, validation_alias="HIRESENSE_DEBUG")

    # ---- Database ----
    MONGODB_URI: str
    DATABASE_NAME: str

    # ---- Auth ----
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- AI ----
    GEMINI_API_KEY: SecretStr = Field(default=SecretStr("your_gemini_api_key_here"))
    OPENAI_API_KEY: SecretStr = Field(default=SecretStr("your_openai_api_key_here"))

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

    lru_cache ensures the .env file is parsed only once per process,
    and this function can be used as a FastAPI dependency
    (Depends(get_settings)) for clean DI instead of importing
    a global singleton everywhere.
    """
    return Settings()


settings = get_settings()
