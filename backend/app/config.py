from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_MODE: str = "polling"
    TELEGRAM_ALLOWED_CHANNEL_IDS: str = ""
    TELEGRAM_POLL_TIMEOUT_SECONDS: int = 30
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    CLUSTER_SIMILARITY_THRESHOLD: float = 0.55
    EDGE_DECAY_THRESHOLD: float = 0.40
    WATCHLIST_SCAN_INTERVAL_SECONDS: int = 300
    R_CLAIM_WINDOW_HOURS: float = 6.0
    MIN_ACTIVE_NODES_FOR_R_CLAIM: int = 5
    BURSTINESS_INTER_ARRIVAL_THRESHOLD_SECONDS: float = 60.0
    API_KEY: str | None = None
    ANTHROPIC_TIMEOUT_SECONDS: float = 30.0
    ANTHROPIC_MAX_RETRIES: int = 3
    ANTHROPIC_RETRY_BASE_SECONDS: float = 1.0

    @field_validator("EMBEDDING_MODEL", mode="before")
    @classmethod
    def default_embedding_model(cls, value: str | None) -> str:
        if not value or not str(value).strip():
            return "paraphrase-multilingual-MiniLM-L12-v2"
        return str(value).strip()

    @field_validator("DATABASE_URL")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value

    class Config:
        env_file = ".env"

settings = Settings()
