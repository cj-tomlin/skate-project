from pathlib import Path

from pydantic_core import Url

# Basic settings
HOSTNAME: str = "127.0.0.1"
PORT: int = 8000
PROJECT_NAME: str = "Skate Backend"

# Paths
PROJECT_REL_PATH: Path = Path(__file__).resolve()
DATA_VOLUME_ROOT: Path = PROJECT_REL_PATH / "app" / "data"
STATIC_VOLUME_ROOT: Path = PROJECT_REL_PATH / "app" / "static"

# For frontend (might not even be right)
STATIC_BASE_URL: Url = Url(f"http://localhost:{PORT}/static")

# Logging settings
LOG_LEVEL: str = "INFO"