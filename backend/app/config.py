"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    # ============================================
    # Backend Configuration
    # ============================================
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/lotus.db"

    # ============================================
    # LLM Configuration
    # ============================================
    # Claude API (Anthropic)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.7

    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # LLM Strategy
    USE_LOCAL_LLM_FOR_CLASSIFICATION: bool = True
    USE_CLAUDE_FOR_INFERENCE: bool = True

    # ============================================
    # Integration APIs
    # ============================================
    # Slack OAuth
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    SLACK_REDIRECT_URI: str = "http://localhost:8000/auth/slack/callback"
    SLACK_BOT_TOKEN: str = ""
    SLACK_USER_TOKEN: str = ""

    # Google OAuth (for Google Meet transcripts)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # ============================================
    # Security
    # ============================================
    # Encryption key for sensitive data in database
    ENCRYPTION_KEY: str = ""

    # JWT Secret for API authentication (Phase 2)
    JWT_SECRET: str = "change-this-to-a-random-secret-key-in-production"

    # ============================================
    # Application Settings
    # ============================================
    # Task Inference
    MIN_CONFIDENCE_THRESHOLD: int = 70
    BATCH_PROCESSING_SIZE: int = 10
    MAX_MESSAGES_PER_SYNC: int = 100

    # Rate Limiting
    MAX_CLAUDE_CALLS_PER_DAY: int = 50
    RATE_LIMIT_WINDOW_HOURS: int = 24

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./data/logs/lotus.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_SLACK_INGESTION: bool = True
    ENABLE_GOOGLE_MEET_INGESTION: bool = False
    ENABLE_CONTEXT_WEAVER: bool = False
    ENABLE_PRIORITY_ORCHESTRATOR: bool = False

    # ============================================
    # ChromaDB (Vector Database)
    # ============================================
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "lotus_messages"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Create global settings instance
settings = Settings()
