"""Application settings and configuration."""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: Literal["development", "production"] = "development"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0

    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # LLM Provider API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None

    # Default LLM Settings
    default_llm_provider: Literal["openai", "anthropic", "azure"] = "openai"
    default_model: str = "gpt-4-turbo-preview"
    default_temperature: float = 0.7
    default_max_tokens: int = 4000

    # Budget Controls (USD)
    default_user_budget: float = 100.00
    budget_warning_threshold: float = 0.80
    budget_reset_period: Literal["daily", "weekly", "monthly"] = "monthly"

    # Session Configuration
    session_ttl_hours: int = 24
    session_cleanup_interval_minutes: int = 60

    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    workers: int = 4

    # CORS Configuration
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    # MCP Configuration
    mcp_server_name: str = "agentparty"
    mcp_server_version: str = "0.1.0"

    # Paths
    agents_dir: str = "agents"
    workflows_dir: str = "workflows"
    jobs_dir: str = "jobs"

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
