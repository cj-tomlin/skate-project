from pathlib import Path
from pydantic import BaseModel, Field, PostgresDsn, RedisDsn, computed_field
from pydantic_core import Url


class BaseSettings(BaseModel):
    """Base settings class for application configuration."""

    # Environment
    ENV: str = Field(
        "development", description="Environment (development, testing, production)"
    )
    DEBUG: bool = Field(True, description="Debug mode")

    # Application
    APP_NAME: str = Field("Skate Backend", description="Application name")
    APP_VERSION: str = Field("0.1.0", description="Application version")
    HOSTNAME: str = Field("127.0.0.1", description="Hostname")
    PORT: int = Field(8000, description="Port")

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

    @computed_field
    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "app" / "data"

    @computed_field
    @property
    def STATIC_DIR(self) -> Path:
        return self.BASE_DIR / "app" / "static"

    # Static URL
    @computed_field
    @property
    def STATIC_BASE_URL(self) -> Url:
        return Url(f"http://localhost:{self.PORT}/static")

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # Security
    SECRET_KEY: str = Field(
        "ae0c90b0d5b0dd6299b85fcc24ec8971df648133b74f164db23b86ef0806d0a5",
        description="Secret key for JWT and other security features",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, description="Minutes before access token expires"
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(["*"], description="CORS allowed origins")
    CORS_METHODS: list[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "PATCH"], description="CORS allowed methods"
    )
    CORS_HEADERS: list[str] = Field(["*"], description="CORS allowed headers")

    # Database
    POSTGRES_USER: str = Field("skate_user", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field("skate_password", description="PostgreSQL password")
    POSTGRES_DB: str = Field("skate_db", description="PostgreSQL database name")
    POSTGRES_HOST: str = Field("localhost", description="PostgreSQL host")
    POSTGRES_PORT: str = Field("5432", description="PostgreSQL port")

    @computed_field
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Test Database
    POSTGRES_TEST_USER: str = Field(
        "skate_test_user", description="Test PostgreSQL username"
    )
    POSTGRES_TEST_PASSWORD: str = Field(
        "skate_test_password", description="Test PostgreSQL password"
    )
    POSTGRES_TEST_DB: str = Field(
        "skate_test_db", description="Test PostgreSQL database name"
    )
    POSTGRES_TEST_PORT: str = Field("5433", description="Test PostgreSQL port")

    @computed_field
    @property
    def TEST_DATABASE_URL(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.POSTGRES_TEST_USER}:{self.POSTGRES_TEST_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_TEST_PORT}/{self.POSTGRES_TEST_DB}"
        )

    # Redis
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: str = Field("6379", description="Redis port")

    @computed_field
    @property
    def REDIS_URL(self) -> RedisDsn:
        return RedisDsn(f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
