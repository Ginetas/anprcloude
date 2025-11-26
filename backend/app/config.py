"""
Configuration Management
Handles all application settings using Pydantic Settings with environment variables.
"""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="ANPR Cloud Backend", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment (development, staging, production)")

    # API
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow credentials")
    cors_methods: List[str] = Field(default=["*"], description="Allowed HTTP methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed HTTP headers")

    # Database - PostgreSQL
    postgres_server: str = Field(default="localhost", description="PostgreSQL server")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_user: str = Field(default="anpr", description="PostgreSQL user")
    postgres_password: str = Field(default="anpr_password", description="PostgreSQL password")
    postgres_db: str = Field(default="anpr_db", description="PostgreSQL database name")
    postgres_echo: bool = Field(default=False, description="Echo SQL statements")

    # Connection pool settings
    db_pool_size: int = Field(default=5, description="Database connection pool size")
    db_max_overflow: int = Field(default=10, description="Database max overflow connections")
    db_pool_timeout: int = Field(default=30, description="Database pool timeout in seconds")
    db_pool_recycle: int = Field(default=3600, description="Database pool recycle time in seconds")

    # Redis
    redis_host: str = Field(default="localhost", description="Redis server")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_ttl: int = Field(default=3600, description="Redis default TTL in seconds")

    # File Storage
    upload_dir: str = Field(default="/var/anpr/uploads", description="Upload directory path")
    max_upload_size: int = Field(default=10485760, description="Max upload size in bytes (10MB)")
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp"],
        description="Allowed image MIME types"
    )

    # WebSocket
    ws_heartbeat_interval: int = Field(default=30, description="WebSocket heartbeat interval in seconds")
    ws_max_connections: int = Field(default=100, description="Max WebSocket connections")

    # Event Processing
    event_retention_days: int = Field(default=90, description="Event retention period in days")
    event_batch_size: int = Field(default=100, description="Event batch processing size")

    # Exporter Settings
    exporter_timeout: int = Field(default=30, description="Exporter HTTP timeout in seconds")
    exporter_retry_attempts: int = Field(default=3, description="Exporter retry attempts")
    exporter_retry_delay: int = Field(default=5, description="Exporter retry delay in seconds")

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format"
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")

    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, description="Metrics endpoint port")

    @property
    def database_url(self) -> str:
        """Build PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def async_database_url(self) -> str:
        """Build async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Build Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    def model_dump_safe(self) -> Dict[str, Any]:
        """Dump settings without sensitive information."""
        data = self.model_dump()
        sensitive_keys = ["postgres_password", "redis_password", "secret_key"]
        for key in sensitive_keys:
            if key in data:
                data[key] = "***REDACTED***"
        return data


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()


# Export settings instance
settings = get_settings()
