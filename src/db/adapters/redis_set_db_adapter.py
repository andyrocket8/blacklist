import logging

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.db.adapters.base_set_db_adapter import ISetDbAdapter
from src.db.adapters.base_set_db_adapter import SetDbAdapterError


class RedisSetDbAdapter(ISetDbAdapter[str]):
    """Set management adapter for Redis with keys as str"""

    def __init__(self, db: RedisAsyncio):
        self.__db = db

    async def add_set(self, set_id: str) -> int:
        """Return 1 on empty set (in terms of Redis NO SET)"""
        return 0 if await self.exists(set_id) else 1

    async def del_set(self, set_id: str) -> int:
        try:
            return await self.__db.delete(set_id)
        except RedisError as e:
            logging.error('On redis delete set operation error occurred, details: %s', str(e))
            raise SetDbAdapterError('Redis DB Error, details: {}'.format(str(e))) from None

    async def copy_set(self, source_set_id: str, target_set_id: str, with_replace: bool = False) -> int:
        try:
            return await self.__db.copy(
                source_set_id,
                target_set_id,
                replace=with_replace,
            )
        except RedisError as e:
            logging.error('On redis copy set operation error occurred, details: %s', str(e))
            raise SetDbAdapterError('Redis DB Error, details: {}'.format(str(e))) from None

    async def exists(self, set_id: str) -> bool:
        return await self.__db.exists(set_id) == 1
