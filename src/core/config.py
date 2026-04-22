import os
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class BaseConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        extra="ignore",
        frozen=True,
        env_nested_delimiter="__",
        case_sensitive=False,
    )

class Settings(BaseConfigSettings):
    app_version: str = "0.1.0"
    debug: bool = True
    environment: Literal["development", "staging", "production"] = "development"
    service_name: str = "rag-api"

    # Default values match if not provided in .env
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mypassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "fastapidb"

    @property
    def database_url(self) -> str:
        # Note the use of postgresql+asyncpg://
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ChromaDB connection settings match what we have in compose.yaml
    CHROMA_HOST:str = "localhost"
    CHROMA_PORT:str = "8000"
    EMBEDDING_MODEL:str = "gemini-embedding-2-preview"

    # Retriever and Reranker settings
    retriever_top_k: int = 10
    reranker_top_k: int = 10

    # Langfuse
    
    

def get_settings() -> Settings:
    return Settings()