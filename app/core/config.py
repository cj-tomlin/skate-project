from pathlib import Path
from pydantic import BaseSettings, Field, HttpUrl


# Environment settings
class Settings(BaseSettings):
    """
    Application settings.

    Uses Pydantic's BaseSettings for environment variable loading.
    """

    # Environment
    ENV: str = Field("development", env="ENV")
    DEBUG: bool = Field(True, env="DEBUG")

    # Basic settings
    HOSTNAME: str = Field("127.0.0.1", env="HOSTNAME")
    PORT: int = Field(8000, env="PORT")
    APP_NAME: str = Field("Skate Backend", env="APP_NAME")
    APP_VERSION: str = Field("0.1.0", env="APP_VERSION")

    # Security settings
    SECRET_KEY: str = Field(
        "ae0c90b0d5b0dd6299b85fcc24ec8971df648133b74f164db23b86ef0806d0a5",
        env="SECRET_KEY",
    )

    # Paths
    PROJECT_REL_PATH: Path = Path(__file__).resolve().parent.parent
    DATA_VOLUME_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / "app" / "data"
    )
    STATIC_VOLUME_ROOT: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
        / "app"
        / "static"
    )

    # Static URL for frontend
    STATIC_BASE_URL: HttpUrl = Field(
        "http://localhost:8000/static", env="STATIC_BASE_URL"
    )

    # Logging settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # Database settings
    POSTGRES_USER: str = Field("skate_user", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("skate_password", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("skate_db", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field("5432", env="POSTGRES_PORT")

    # Test database settings
    POSTGRES_TEST_USER: str = Field("skate_test_user", env="POSTGRES_TEST_USER")
    POSTGRES_TEST_PASSWORD: str = Field(
        "skate_test_password", env="POSTGRES_TEST_PASSWORD"
    )
    POSTGRES_TEST_DB: str = Field("skate_test_db", env="POSTGRES_TEST_DB")
    POSTGRES_TEST_PORT: str = Field("5433", env="POSTGRES_TEST_PORT")

    # Redis settings
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: str = Field("6379", env="REDIS_PORT")

    # Computed properties
    @property
    def DATABASE_URL(self) -> str:
        """Get the database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        """Get the test database URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_TEST_PORT}/{self.POSTGRES_TEST_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Get the Redis URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()
