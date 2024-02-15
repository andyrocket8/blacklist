# Redis database connector classes
from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator

from redis.asyncio import Redis as RedisAsyncio

from src.core.config import app_settings

from .redis_db_pool import RedisConnectionPool
from .redis_db_pool import context_async_redis_pool_client
from .redis_db_pool import redis_pool_client

# init connection pool
connection_pool_obj = RedisConnectionPool(app_settings)


async def redis_client() -> AsyncGenerator[RedisAsyncio, None]:
    """
    Wrapper for generator for obtaining redis client (with global module variable)
    # TODO change to abstract connection factory
    :rtype AsyncGenerator[RedisAsyncio, None]
    """
    async for client in redis_pool_client(connection_pool_obj):
        yield client


def context_async_redis_client(job_name: str) -> AbstractAsyncContextManager:
    return context_async_redis_pool_client(connection_pool_obj, job_name)
