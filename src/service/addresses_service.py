import logging
from ipaddress import IPv4Address
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast
from uuid import UUID

from src.core.settings import ALLOWED_ADDRESSES_SET_ID
from src.core.settings import BATCH_SIZE
from src.core.settings import BLACK_LIST_ADDRESSES_SET_ID
from src.db.redis_db import RedisAsyncio

T = TypeVar('T')
TypeT = Type[T]


async def iter_over_records(iter_records: list[T]) -> AsyncGenerator[tuple[int, str], None]:
    """Iterate over recordset"""
    flush_counter = 0
    board_value = BATCH_SIZE
    for value in iter_records:
        flush_counter += 1
        yield board_value == flush_counter, str(value)
        if board_value == flush_counter:
            flush_counter = 0


class AbstractDBService(Generic[T]):
    """Serve operations with abstract classes in Redis database"""

    service_type: TypeT
    set_id: UUID

    def __init__(self, db: RedisAsyncio, set_id: Optional[UUID] = None):
        self.db: RedisAsyncio = db
        self.set_id: UUID = set_id if set_id is not None else self.set_id

    async def get_records(self, records_count: int = 0, all_records: bool = True) -> list[T]:
        """Getting records from database"""
        result = []
        set_id: str = str(self.set_id)
        logging.debug('Getting records from Redis database, set ID: %s', set_id)
        current_record = 0
        async for record in self.db.sscan_iter(name=set_id, match='*'):
            result.append(self.service_type(*[record]))
            if not all_records and records_count > 0:
                current_record += 1
                if current_record >= records_count:
                    break
        logging.debug('Retrieved %s records from Redis database, set ID: %s', len(result), set_id)
        return result

    async def write_set(self, set_data: list[str]) -> int:
        """Asynchronously write data to Redis set"""
        set_id: str = str(self.set_id)
        logging.debug('Saving %d records to Redis database, set ID: %s', len(set_data), set_id)
        return await cast(Awaitable[Any], self.db.sadd(set_id, *set_data))

    async def write_records(self, records: list[T]) -> int:
        """Saving records to database
        Split data into pieces and write these chunks to Redis DB
        """
        saved_records = 0
        records_to_add: list[str] = []
        async for need_flush, record in iter_over_records(records):
            records_to_add.append(record)
            if need_flush:
                await self.write_set(records_to_add)
                saved_records += len(records_to_add)
                records_to_add = []
        if len(records_to_add):
            await self.write_set(records_to_add)
            saved_records += len(records_to_add)
        logging.debug('Total wrote %d records to Redis database', saved_records)
        return saved_records

    async def del_set(self, set_data: list[str]) -> int:
        """Asynchronously delete data from Redis set"""
        set_id: str = str(self.set_id)
        logging.debug('Deleting %d records from Redis database, set ID: %s', len(set_data), set_id)
        return await cast(Awaitable[Any], self.db.srem(set_id, *set_data))

    async def del_records(self, records: list[T]) -> int:
        """Delete records from database
        Split data into pieces and delete these chunks from Redis DB
        """
        deleted_records = 0
        records_to_delete: list[str] = []
        async for need_flush, record in iter_over_records(records):
            records_to_delete.append(record)
            if need_flush:
                await self.del_set(records_to_delete)
                deleted_records += len(records_to_delete)
                records_to_delete = []
        if len(records_to_delete):
            await self.del_set(records_to_delete)
            deleted_records += len(records_to_delete)
        logging.debug('Total deleted %d records from Redis database', deleted_records)
        return deleted_records

    async def count(self) -> int:
        set_id: str = str(self.set_id)
        logging.debug('Counting records in Redis database, set ID: %s', set_id)
        return await cast(Awaitable[Any], self.db.scard(set_id))


class BlackListAddressesDBService(AbstractDBService[IPv4Address]):
    """Serve operations with black list addresses in Redis database"""

    service_type = IPv4Address
    set_id = BLACK_LIST_ADDRESSES_SET_ID


class AllowedAddressesDBService(AbstractDBService[IPv4Address]):
    """Serve operations with allowed addresses in Redis database"""

    service_type = IPv4Address
    set_id = ALLOWED_ADDRESSES_SET_ID
