# Redis database connector classes
import logging
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncGenerator

from redis.asyncio import ConnectionPool
from redis.asyncio import Redis as RedisAsyncio

from src.core.config import AppSettings
from src.core.config import app_settings


class RedisConnectionPool:
    """Redis connection class"""

    def __init__(self, application_settings: AppSettings):
        kwargs: dict[str, Any] = dict()
        kwargs['decode_responses'] = True
        if application_settings.redis_use_authentication:
            kwargs['username'] = application_settings.redis_username
            kwargs['password'] = application_settings.redis_password
        logging.debug('Creating redis connection pool')
        self.connection_pool: ConnectionPool = ConnectionPool.from_url(
            application_settings.get_redis_uri(),
            **kwargs,
        )

    def __del__(self):
        if logging:
            logging.debug('Closing redis connection pool')


# init connection
connection_pool_obj = RedisConnectionPool(app_settings)


async def redis_client() -> AsyncGenerator[RedisAsyncio, None]:
    """
    Generator for obtaining redis client
    :rtype AsyncGenerator[RedisAsyncio, None]
    """
    client = RedisAsyncio.from_pool(connection_pool_obj.connection_pool)
    logging.debug('Obtaining redis client connection')
    try:
        yield client
    finally:
        if client.connection or client.connection_pool:
            logging.debug('Closing redis client connection')
            await client.aclose()


@asynccontextmanager
async def context_async_redis_client(job_name: str) -> AsyncGenerator[RedisAsyncio, None]:
    """Connection manager for async jobs (auth checks, celery jobs)"""
    client = RedisAsyncio.from_pool(connection_pool_obj.connection_pool)
    logging.debug('Obtaining redis client connection for %s job', job_name)
    try:
        yield client
    finally:
        logging.debug('Closing redis client connection for %s job', job_name)
        await client.aclose()
