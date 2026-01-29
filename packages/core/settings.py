"""
Shared settings configuration.
"""
import os
from dataclasses import dataclass

@dataclass
class Settings:
    """Core application settings."""
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/fitness")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"