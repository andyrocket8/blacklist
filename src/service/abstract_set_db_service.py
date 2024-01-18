import logging
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast
from uuid import UUID

from src.core.settings import BATCH_SIZE
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


class AbstractSetDBService(Generic[T]):
    """Serve operations with abstract classes in Redis database"""

    service_type: TypeT
    set_id: UUID

    def __init__(self, db: RedisAsyncio, set_id: Optional[UUID] = None):
        self.db: RedisAsyncio = db
        self.set_id: UUID = set_id if set_id is not None else self.set_id

    async def fetch_records(self, set_id: Optional[str] = None) -> AsyncGenerator[T, None]:
        """Generator for fetching data from linked set"""
        set_id = str(self.set_id) if set_id is None else set_id
        async for record in self.db.sscan_iter(name=set_id, match='*'):
            yield self.service_type(*[record])

    async def get_records_gen(self, records_count: int = 0, all_records: bool = True) -> AsyncGenerator[T, None]:
        current_record = 0
        async for record in self.fetch_records():
            yield record
            if not all_records and records_count > 0:
                current_record += 1
                if current_record >= records_count:
                    break

    async def get_records(self, records_count: int = 0, all_records: bool = True) -> list[T]:
        """Getting records from database"""
        result = []
        set_id: str = str(self.set_id)
        logging.debug('Getting records from Redis database, set ID: %s', set_id)
        async for record in self.get_records_gen(records_count, all_records):
            result.append(record)
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
                iter_written = await self.write_set(records_to_add)
                saved_records += iter_written
                records_to_add = []
        if len(records_to_add):
            iter_written = await self.write_set(records_to_add)
            saved_records += iter_written
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
                iter_deleted = await self.del_set(records_to_delete)
                deleted_records += iter_deleted
                records_to_delete = []
        if len(records_to_delete):
            iter_deleted = await self.del_set(records_to_delete)
            deleted_records += iter_deleted
        logging.debug('Total deleted %d records from Redis database', deleted_records)
        return deleted_records

    async def count(self) -> int:
        set_id: str = str(self.set_id)
        logging.debug('Counting records in Redis database, set ID: %s', set_id)
        return await cast(Awaitable[Any], self.db.scard(set_id))


AbstractSetDBServiceType = TypeVar('AbstractSetDBServiceType', bound=AbstractSetDBService)
