# Redis connection pool and mixed routines
import logging
from contextlib import asynccontextmanager
from typing import Any
from typing import AsyncGenerator
from uuid import UUID
from uuid import uuid4

from redis.asyncio import ConnectionPool
from redis.asyncio import Redis as RedisAsyncio

from src.core.config_redis import RedisConfig


class RedisConnectionPool:
    """Redis connection class"""

    def __init__(self, redis_settings: RedisConfig):
        kwargs: dict[str, Any] = dict()
        kwargs['decode_responses'] = True
        if redis_settings.redis_use_authentication:
            kwargs['username'] = redis_settings.redis_username
            kwargs['password'] = redis_settings.redis_password
        logging.debug('Creating redis connection pool')
        self.connection_pool: ConnectionPool = ConnectionPool.from_url(
            redis_settings.get_redis_uri(),
            **kwargs,
        )

    def __del__(self):
        if logging:
            logging.debug('Closing redis connection pool')


async def redis_pool_client(connection_pool_obj: RedisConnectionPool) -> AsyncGenerator[RedisAsyncio, None]:
    """
    Generator for obtaining redis client
    :rtype AsyncGenerator[RedisAsyncio, None]
    """
    redis_client_id: UUID = uuid4()
    client = RedisAsyncio(connection_pool=connection_pool_obj.connection_pool)
    logging.debug('Obtaining redis client connection, client ID: %s', redis_client_id)
    try:
        yield client
    finally:
        logging.debug('Closing redis client connection, client ID: %s', redis_client_id)
        await client.aclose(close_connection_pool=False)


@asynccontextmanager
async def context_async_redis_pool_client(
    connection_pool_obj: RedisConnectionPool, job_name: str
) -> AsyncGenerator[RedisAsyncio, None]:
    """Connection manager for async jobs (auth checks, celery jobs)"""
    redis_client_id: UUID = uuid4()
    client: RedisAsyncio = RedisAsyncio(connection_pool=connection_pool_obj.connection_pool)
    logging.debug('Obtaining redis client connection for %s job, client ID: %s', job_name, redis_client_id)
    try:
        yield client
    finally:
        logging.debug('Closing redis client connection for %s job, client ID: %s', job_name, redis_client_id)
        await client.aclose(close_connection_pool=False)
