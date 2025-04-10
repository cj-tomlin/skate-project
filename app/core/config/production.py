from app.core.config.base import BaseSettings


class ProductionSettings(BaseSettings):
    """Production-specific settings."""

    ENV: str = "production"
    DEBUG: bool = False

    # Security settings
    CORS_ORIGINS: list[str] = ["https://your-production-domain.com"]

    # In production, these should be set via environment variables
    # and not hardcoded in the source code
    SECRET_KEY: str = ""  # Will be overridden by env var

    # Database settings should come from environment variables in production
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: str = ""
