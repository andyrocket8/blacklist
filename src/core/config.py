from logging import config as logging_config
from os import path as os_path
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from .logger import LOGGING

# Logging settings from logger.py
logging_config.dictConfig(LOGGING)

# Project root. It's vital to set work folder to project root for proper .env file location
BASE_DIR: Path = Path(os_path.dirname(os_path.dirname(os_path.abspath(__file__))))


class AppSettings(BaseSettings):
    host: str = 'localhost'  # application host
    port: int = 8000  # application port
    root_path: str = '/'  # root path for ASGI application (proxy prefix)
    app_title: str = 'Black list processor'  # application title
    use_redis_storage: bool = True  # use Redis database for storing black lists
    redis_host: str = 'localhost'  # redis host
    redis_port: int = 6379  # redis port
    redis_db: int = 0  # redis DB number
    # TODO add redis authentication
    redis_use_authentication: bool = False  # Not implemented yet!
    redis_username: str = ''  # redis authentication username
    redis_password: str = ''  # redis authentication password
    show_openapi: bool = True  # if you want to hide API docs set False here
    use_authorization: bool = False  # set True to use method authorization with tokens
    # Max entries in address change history. <None> for no limits in history depth, 0 - no history at all
    history_depth: Optional[int] = None

    class Config:
        env_file = '.env'

    def get_redis_uri(self):
        return f'redis://{self.redis_host}:{self.redis_port}?db={self.redis_db}'

    def get_redis_uri_for_celery(self):
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'


# Application settings from .env file
app_settings = AppSettings()
