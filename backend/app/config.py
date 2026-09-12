from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-mpnet-base-v2"
    CLUSTER_SIMILARITY_THRESHOLD: float = 0.75
    EDGE_DECAY_THRESHOLD: float = 0.40
    WATCHLIST_SCAN_INTERVAL_SECONDS: int = 300
    R_CLAIM_WINDOW_HOURS: float = 6.0
    MIN_ACTIVE_NODES_FOR_R_CLAIM: int = 5
    BURSTINESS_INTER_ARRIVAL_THRESHOLD_SECONDS: float = 60.0
    API_KEY: str | None = None
    ANTHROPIC_TIMEOUT_SECONDS: float = 30.0
    ANTHROPIC_MAX_RETRIES: int = 3
    ANTHROPIC_RETRY_BASE_SECONDS: float = 1.0

    class Config:
        env_file = ".env"

settings = Settings()
