from pathlib import Path
from pydantic_core import Url
import os

# TODO: Improve secret management and environment configuration

# Basic settings
HOSTNAME: str = "127.0.0.1"
PORT: int = 8000
PROJECT_NAME: str = "Skate Backend"

# Security settings (Move to env file or Docker in the future)
# Generate with production_data script before deploying
SECRET_KEY: str = "ae0c90b0d5b0dd6299b85fcc24ec8971df648133b74f164db23b86ef0806d0a5"

# Paths
PROJECT_REL_PATH: Path = (
    Path(__file__).resolve().parent.parent
)  # Adjust path for your project structure
DATA_VOLUME_ROOT: Path = PROJECT_REL_PATH / "app" / "data"
STATIC_VOLUME_ROOT: Path = PROJECT_REL_PATH / "app" / "static"

# Static URL for frontend (optional)
STATIC_BASE_URL: Url = Url(f"http://localhost:{PORT}/static")

# Logging settings
LOG_LEVEL: str = "INFO"

# Database settings
POSTGRES_USER = os.getenv("POSTGRES_USER", "skate_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "skate_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "skate_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
