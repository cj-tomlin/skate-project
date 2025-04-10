from app.core.config.base import BaseSettings


class TestingSettings(BaseSettings):
    """Testing-specific settings."""

    ENV: str = "testing"
    DEBUG: bool = True

    # Use test database by default
    POSTGRES_USER: str = "skate_test_user"
    POSTGRES_PASSWORD: str = "skate_test_password"
    POSTGRES_DB: str = "skate_test_db"
    POSTGRES_PORT: str = "5433"
