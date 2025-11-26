from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "ANPR System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://anpr:anpr@localhost:5432/anpr"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30

    # Security
    SECRET_KEY: str = "change-this-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
