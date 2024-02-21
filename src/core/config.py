from logging import config as logging_config
from os import path as os_path
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from .config_redis import RedisConfig
from .logger import LOGGING

# Logging settings from logger.py
logging_config.dictConfig(LOGGING)

# Project root. It's vital to set work folder to project root for proper .env file location
BASE_DIR: Path = Path(os_path.dirname(os_path.dirname(os_path.abspath(__file__))))


class AppSettings(BaseSettings, RedisConfig):
    host: str = 'localhost'  # application host
    port: int = 8000  # application port
    root_path: str = '/'  # root path for ASGI application (proxy prefix)
    app_title: str = 'Black list processor'  # application title
    use_redis_storage: bool = True  # use Redis database for storing black lists
    show_openapi: bool = True  # if you want to hide API docs set False here
    use_authorization: bool = False  # set True to use method authorization with tokens
    # Max entries in address change history. <None> for no limits in history depth, 0 - no history at all
    history_depth: Optional[int] = None

    class Config:
        env_file = '.env'


# Application settings from .env file
app_settings = AppSettings()
