import logging
from datetime import timedelta as dt_timedelta
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import cast
from uuid import UUID
from uuid import uuid4

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.core.settings import SET_EXPIRE_SECONDS
from src.models.abstract_types import K
from src.models.abstract_types import T
from src.models.abstract_types import TypeT
from src.utils.time_utils import get_current_time_with_tz

from .abstract_set_db import AbstractDBSet
from .abstract_set_db import AbstractSetDbError


class RedisSetDBError(AbstractSetDbError):
    pass


class RedisSetDB(AbstractDBSet, Generic[K, T]):
    """Redis DB Storage with Sets"""

    service_type: TypeT
    new_id_creator: Callable[[], K]

    def __init__(self, db: RedisAsyncio):
        self.__db: RedisAsyncio = db

    async def del_from_set(self, set_id: K, deleted_data: Iterable[T]) -> int:
        """Asynchronously delete data from Redis set"""
        str_set_id: str = str(set_id)
        deleted_data_t = tuple(str(x) for x in deleted_data)
        logging.debug('Deleting %d records from Redis database, set ID: %s', len(deleted_data_t), str_set_id)
        try:
            return await cast(Awaitable[Any], self.__db.srem(str_set_id, *deleted_data_t))
        except RedisError as e:
            logging.error('On redis set deletion operation error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def write_to_set(self, set_id: K, changed_data: Iterable[T]) -> int:
        """Asynchronously write data to Redis set"""
        str_set_id: str = str(set_id)
        changed_data_t = tuple(str(x) for x in changed_data)
        logging.debug('Saving %d records to Redis database, set ID: %s', len(changed_data_t), set_id)
        try:
            return await cast(Awaitable[Any], self.__db.sadd(str_set_id, *changed_data_t))
        except RedisError as e:
            logging.error('On redis set write operation error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def __fetch_one_set(self, set_id: K) -> AsyncGenerator[T, None]:
        """Fetch from one set (default option)"""
        str_set_id = str(set_id)
        try:
            async for record in self.__db.sscan_iter(name=str_set_id, match='*'):
                yield self.service_type(*[record])
        except RedisError as e:
            logging.error('On redis fetching error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def __merge_sets(self, set_id: K, *set_ids_to_union: K) -> K:
        """Merge sets and return set ID"""

        sets_to_merge: tuple[str, ...] = (str(set_id),) + tuple([str(x) for x in set_ids_to_union])
        merged_set_id = self.new_id_creator()
        try:
            logging.debug('Merging sets to new, set ID: %s', merged_set_id)
            records_merged: int = await cast(
                Awaitable[Any], self.__db.sunionstore(str(merged_set_id), list(sets_to_merge))
            )
            logging.debug('Sets merged, records count: %d, set ID: %s', records_merged, merged_set_id)
            logging.debug(
                'Setting set expire time to %s, set ID: %s',
                get_current_time_with_tz() + dt_timedelta(seconds=SET_EXPIRE_SECONDS),
            )
            await self.__db.expire(str(merged_set_id), SET_EXPIRE_SECONDS)
            return merged_set_id
        except RedisError as e:
            logging.error('On redis fetching error occurred, details: %s', str(e))
            raise RedisSetDBError('Redis DB Error, details: {}'.format(str(e)))

    async def fetch_records(self, set_id: K, *set_ids_to_union: K) -> AsyncGenerator[T, None]:
        remove_set, fetching_set = False, set_id
        if len(set_ids_to_union):
            fetching_set = await self.__merge_sets(set_id, *set_ids_to_union)
            remove_set = True
        try:
            async for record in self.__fetch_one_set(fetching_set):
                yield record
        finally:
            if remove_set:
                # Explicitly remove temporarily set
                await self.remove_set(fetching_set)

    async def remove_set(self, set_id: K):
        """Remove set"""
        str_set_id = str(set_id)
        try:
            logging.debug('Removing set on demand, set ID: %s', str_set_id)
            await self.__db.delete(str_set_id)
        except RedisError as e:
            logging.error('On redis set deletion error occurred, set ID: %s, details: %s', str_set_id, str(e))
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
    new_id_creator = uuid4


class IpNetworkRedisSetDB(RedisSetDB[UUID, IPv4Network]):
    service_type = IPv4Network
    new_id_creator = uuid4


class UUIDRedisSetDB(RedisSetDB[UUID, UUID]):
    service_type = UUID
    new_id_creator = uuid4
