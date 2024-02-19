import logging
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Iterable
from typing import cast

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.db.base_set_db_entity import ISetDbEntity
from src.db.base_set_db_entity import SetDbIdentityError


class RedisSetDbEntityAdapter(ISetDbEntity[str, str]):
    """Entity Set management adapter for Redis with keys as str, values as str"""

    def __init__(self, db: RedisAsyncio):
        self.__db = db

    async def add_to_set(self, set_id: str, added_data: Iterable[str]) -> int:
        """Add data to set"""
        changed_data_t: tuple[str, ...] = tuple(x for x in added_data)
        logging.debug('Saving %d records to Redis database, set ID: %s', len(changed_data_t), set_id)
        try:
            return await cast(Awaitable[Any], self.__db.sadd(set_id, *changed_data_t))
        except RedisError as e:
            logging.error('On redis set write operation error occurred, details: %s', str(e))
            raise SetDbIdentityError('Redis DB Error, details: {}'.format(str(e))) from None

    async def del_from_set(self, set_id: str, deleted_data: Iterable[str]) -> int:
        """Remove data from Redis Set"""
        deleted_data_t: tuple[str, ...] = tuple(x for x in deleted_data)
        logging.debug('Deleting %d records from Redis database, set ID: %s', len(deleted_data_t), set_id)
        try:
            return await cast(Awaitable[Any], self.__db.srem(set_id, *deleted_data_t))
        except RedisError as e:
            logging.error('On redis set deletion operation error occurred, details: %s', str(e))
            raise SetDbIdentityError('Redis DB Error, details: {}'.format(str(e))) from None

    async def fetch_records(self, set_id: str) -> AsyncGenerator[str, None]:
        """Fetch data from set"""
        try:
            async for record in self.__db.sscan_iter(name=set_id, match='*'):
                yield record
        except RedisError as e:
            logging.error('On redis fetching error occurred, details: %s', str(e))
            raise SetDbIdentityError('Redis DB Error, details: {}'.format(str(e))) from None

    async def count(self, set_id: str) -> int:
        """Get records count from set"""
        logging.debug('Counting records in Redis database, set ID: %s', set_id)
        try:
            return await cast(Awaitable[Any], self.__db.scard(set_id))
        except RedisError as e:
            logging.error('On redis counting set size error occurred, details: %s', str(e))
            raise SetDbIdentityError('Redis DB Error, details: {}'.format(str(e))) from None

    async def contains(self, set_id: str, value: str) -> bool:
        """Check whether set contains value from set"""
        try:
            return await cast(Awaitable[Any], self.__db.sismember(set_id, value)) == 1
        except RedisError as e:
            logging.error('On redis "sismember" routine execution got an error, details: %s', str(e))
            raise SetDbIdentityError('Redis DB Error, details: {}'.format(str(e))) from None
