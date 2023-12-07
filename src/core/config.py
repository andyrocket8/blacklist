from logging import config as logging_config
from os import path as os_path
from pathlib import Path

from pydantic_settings import BaseSettings

from .logger import LOGGING

# Logging settings from logger.py
logging_config.dictConfig(LOGGING)

# Project root. It's vital to set work folder to project root for proper .env file location
BASE_DIR: Path = Path(os_path.dirname(os_path.dirname(os_path.abspath(__file__))))


class AppSettings(BaseSettings):
    host: str = 'localhost'  # application host
    port: int = 8000  # application port
    app_title: str = 'Black list processor'  # application title
    use_redis_storage: bool = True  # use Redis database for storing black lists
    redis_host: str = 'localhost'  # redis host
    redis_port: int = 6379  # redis port
    redis_db: int = 0  # redis DB number
    redis_use_authentication: bool = False
    redis_username: str = ''  # redis authentication username
    redis_password: str = ''  # redis authentication password
    show_openapi: bool = True  # if you want to hide API docs set False here

    class Config:
        env_file = '.env'

    def get_redis_uri(self):
        return f'redis://{self.redis_host}:{self.redis_port}?db={self.redis_db}'

    def get_redis_uri_for_celery(self):
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'


# Application settings from .env file
app_settings = AppSettings()
