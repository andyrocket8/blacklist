# main conftest.py for application
import logging
from dataclasses import dataclass
from datetime import datetime as dt_datetime
from pathlib import Path
from typing import Generator
from typing import Optional

import pytest
from pydantic_settings import BaseSettings

from src.core.config_redis import RedisConfig
from src.core.settings import REDIS_DOCKER_IMAGE_NAME
from src.utils.subprocess_utils import execute_command
from src.utils.subprocess_utils import logging_sp_exec_error

print('Invoking main conftest.py')


CONTAINER_NAME = f'redis-pytest-{dt_datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]}'


class RedisForTestSettings(BaseSettings, RedisConfig):
    start_redis_cmd: str = f'docker run --rm -d --name {CONTAINER_NAME} -p %:6379 {REDIS_DOCKER_IMAGE_NAME}'
    stop_redis_cmd: str = f'docker stop {CONTAINER_NAME}'


@dataclass
class RedisForTestConfig:
    test_redis_available: bool
    redis_config: Optional[RedisConfig]


class RedisTestServerError(Exception):
    pass


@pytest.fixture(scope='session')
def redis_env_for_test() -> Generator[RedisForTestConfig, None, None]:
    env_file = Path('.test_redis.env')
    if env_file.is_file():
        print('\nStarting redis test server')
        redis_for_test_settings = RedisForTestSettings(_env_file=str(env_file))
        print(f'Redis for test settings: {redis_for_test_settings}')
        # Starting redis test server
        start_redis_command = redis_for_test_settings.start_redis_cmd.replace(
            '%', str(redis_for_test_settings.redis_port)
        )
        return_code, output = execute_command(start_redis_command)
        if return_code:
            logging_sp_exec_error(start_redis_command, return_code, output)
            raise RedisTestServerError('Error on starting test redis server')
        logging.debug('Test redis server started')
        # Now fill in the Redis config options. Extract RedisConfig data from RedisForTestSettings
        yield RedisForTestConfig(True, RedisConfig(**redis_for_test_settings.model_dump()))
        # stopping redis database
        print('\nStopping redis test server')
        stop_redis_command = redis_for_test_settings.stop_redis_cmd
        return_code, output = execute_command(stop_redis_command)
        if return_code:
            logging_sp_exec_error(stop_redis_command, return_code, output)
        else:
            logging.debug('Test redis server stopped')
    else:
        # No redis configuration file detected!
        redis_config_for_test_obj = RedisForTestConfig(False, None)
        yield redis_config_for_test_obj
