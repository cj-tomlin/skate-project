import os
from functools import lru_cache
from typing import Union, Type

from app.core.config.base import BaseSettings
from app.core.config.development import DevelopmentSettings
from app.core.config.testing import TestingSettings
from app.core.config.production import ProductionSettings


@lru_cache()
def get_settings() -> Union[DevelopmentSettings, TestingSettings, ProductionSettings]:
    """
    Get the appropriate settings based on the environment.
    Uses environment variable APP_ENV to determine which settings to load.
    Caches the result for performance.
    """
    env = os.getenv("APP_ENV", "development").lower()

    settings_class: Type[BaseSettings]
    if env == "production":
        settings_class = ProductionSettings
    elif env == "testing":
        settings_class = TestingSettings
    else:  # default to development
        settings_class = DevelopmentSettings

    return settings_class()


# Export settings instance for easy import
settings = get_settings()

# For backward compatibility, export all settings as module-level variables
# This allows existing code to continue working with minimal changes
HOSTNAME = settings.HOSTNAME
PORT = settings.PORT
PROJECT_NAME = settings.APP_NAME
SECRET_KEY = settings.SECRET_KEY
PROJECT_REL_PATH = settings.BASE_DIR
DATA_VOLUME_ROOT = settings.DATA_DIR
STATIC_VOLUME_ROOT = settings.STATIC_DIR
STATIC_BASE_URL = settings.STATIC_BASE_URL
LOG_LEVEL = settings.LOG_LEVEL
DATABASE_URL = settings.DATABASE_URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL
REDIS_URL = settings.REDIS_URL

# Database settings
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_DB = settings.POSTGRES_DB
POSTGRES_HOST = settings.POSTGRES_HOST
POSTGRES_PORT = settings.POSTGRES_PORT

# Test database settings
POSTGRES_TEST_USER = settings.POSTGRES_TEST_USER
POSTGRES_TEST_PASSWORD = settings.POSTGRES_TEST_PASSWORD
POSTGRES_TEST_DB = settings.POSTGRES_TEST_DB
POSTGRES_TEST_PORT = settings.POSTGRES_TEST_PORT

# Redis settings
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
