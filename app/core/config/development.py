from app.core.config.base import BaseSettings


class DevelopmentSettings(BaseSettings):
    """Development-specific settings."""

    ENV: str = "development"
    DEBUG: bool = True

    # Add any development-specific overrides here
