import os
from pydantic_settings import BaseSettings, SettingsConfigDict


ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

ENV_FILE = (
    ".env.production"
    if ENVIRONMENT == "production"
    else ".env.local"
)


class Settings(BaseSettings):
    app_name: str = "Landora API"
    environment: str = ENVIRONMENT

    database_url: str

    openai_api_key: str | None = None
    
    qdrant_url: str
    qdrant_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()