from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI CareerPilot"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str = "sqlite:///./careerpilot.db"
    secret_key: str = Field(default="replace-with-a-long-random-secret-key-at-least-32-characters")
    access_token_expire_minutes: int = 60
    uploads_dir: str = "uploads"

    # AI / LLM configuration. The app must run and degrade gracefully with no key set.
    llm_provider: str = "openai"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: int = 30

    # NLP / semantic search configuration.
    embedding_model: str = "all-MiniLM-L6-v2"
    faiss_index_dir: str = "backend/vector/index_data"

    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key)


settings = Settings()
