import logging
from typing import Type

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.db.adapters.base_set_db_adapter import ISetDbAdapter
from src.db.adapters.base_set_db_adapter import SetDbAdapterError
from src.models.transformation import Transformation
from src.schemas.abstract_types import K


class RedisSetDbAdapter(ISetDbAdapter[K]):
    key_transform: Type[Transformation[K, str]]

    def __init__(self, db: RedisAsyncio):
        self.__db = db

    async def add_set(self, set_id: K) -> int:
        """Return 1 on empty set (in terms of Redis NO SET)"""
        return 0 if await self.exists(set_id) else 1

    async def del_set(self, set_id: K) -> int:
        try:
            return await self.__db.delete(self.key_transform.transform_to_storage(set_id))
        except RedisError as e:
            logging.error('On redis delete set operation error occurred, details: %s', str(e))
            raise SetDbAdapterError('Redis DB Error, details: {}'.format(str(e))) from None

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        try:
            return await self.__db.copy(
                self.key_transform.transform_to_storage(source_set_id),
                self.key_transform.transform_to_storage(target_set_id),
                replace=with_replace,
            )
        except RedisError as e:
            logging.error('On redis copy set operation error occurred, details: %s', str(e))
            raise SetDbAdapterError('Redis DB Error, details: {}'.format(str(e))) from None

    async def exists(self, set_id: K) -> bool:
        return await self.__db.exists(self.key_transform.transform_to_storage(set_id)) == 1
