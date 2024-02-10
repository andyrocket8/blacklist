import logging
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Generic
from typing import Iterable
from typing import cast
from uuid import UUID

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.models.abstract_types import K
from src.models.abstract_types import T
from src.models.abstract_types import TypeT

from .abstract_set_db import AbstractDBSet
from .abstract_set_db import AbstractSetDbError


class RedisSetDBError(AbstractSetDbError):
    pass


class RedisSetDB(AbstractDBSet, Generic[K, T]):
    """Redis DB Storage with Sets"""

    service_type: TypeT

    def __init__(self, db: RedisAsyncio):
        self.__db: RedisAsyncio = db

    async def del_set(self, set_id: K, deleted_data: Iterable[T]) -> int:
        """Asynchronously delete data from Redis set"""
        str_set_id: str = str(set_id)
        deleted_data_t = tuple(str(x) for x in deleted_data)
        logging.debug('Deleting %d records from Redis database, set ID: %s', len(deleted_data_t), str_set_id)
        try:
            return await cast(Awaitable[Any], self.__db.srem(str_set_id, *deleted_data_t))
        except RedisError as e:
            logging.error('On redis set deletion operation error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def write_set(self, set_id: K, changed_data: Iterable[T]) -> int:
        """Asynchronously write data to Redis set"""
        str_set_id: str = str(set_id)
        changed_data_t = tuple(str(x) for x in changed_data)
        logging.debug('Saving %d records to Redis database, set ID: %s', len(changed_data_t), set_id)
        try:
            return await cast(Awaitable[Any], self.__db.sadd(str_set_id, *changed_data_t))
        except RedisError as e:
            logging.error('On redis set write operation error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def fetch_records(self, set_id: K, *set_ids_to_union: K) -> AsyncGenerator[T, None]:
        str_set_id = str(set_id)
        try:
            async for record in self.__db.sscan_iter(name=str_set_id, match='*'):
                yield self.service_type(*[record])
        except RedisError as e:
            logging.error('On redis fetching error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        str_set_id: str = str(set_id)
        logging.debug('Counting records in Redis database, set ID: %s', str_set_id)
        try:
            return await cast(Awaitable[Any], self.__db.scard(str_set_id))
        except RedisError as e:
            logging.error('On redis counting set size error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))


class IpAddressRedisSetDB(RedisSetDB[UUID, IPv4Address]):
    service_type = IPv4Address


class IpNetworkRedisSetDB(RedisSetDB[UUID, IPv4Network]):
    service_type = IPv4Network


class UUIDRedisSetDB(RedisSetDB[UUID, UUID]):
    service_type = UUID
