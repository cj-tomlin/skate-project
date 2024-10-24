from pathlib import Path
from pydantic_core import Url

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
