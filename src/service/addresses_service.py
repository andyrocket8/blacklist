import logging
from ipaddress import IPv4Address
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Optional
from typing import cast
from uuid import UUID

from src.core.settings import ADDRESSES_SET_ID
from src.core.settings import BATCH_SIZE
from src.db.redis_db import RedisAsyncio


class AddressesDBService:
    """Serve operations with addresses in Redis database"""

    def __init__(self, db: RedisAsyncio, addresses_set_id: Optional[UUID] = None):
        self.db: RedisAsyncio = db
        self.addresses_set_id: UUID = addresses_set_id if addresses_set_id is not None else ADDRESSES_SET_ID

    async def get_records(self) -> list[IPv4Address]:
        """Getting records from database"""
        result = []
        set_id: str = str(self.addresses_set_id)
        logging.debug('Getting records from Redis database, set ID: %s', set_id)
        async for record in self.db.sscan_iter(name=set_id, match='*'):
            result.append(IPv4Address(record))
        logging.debug('Retrieved %s records from Redis database, set ID: %s', len(result), set_id)
        return result

    async def write_set(self, set_data: list[str]) -> int:
        """Asynchronously write data to Redis set"""
        set_id: str = str(self.addresses_set_id)
        logging.debug('Saving %d records to Redis database, set ID: %s', len(set_data), set_id)
        return await cast(Awaitable[Any], self.db.sadd(set_id, *set_data))

    async def write_records(self, addresses: list[IPv4Address]) -> int:
        """Saving IPv4 records to database
        Split data into pieces and write these chunks to Redis DB
        """

        async def iter_over_addresses(records: list[IPv4Address]) -> AsyncGenerator[tuple[int, str], None]:
            """Iterate over recordset"""
            flush_counter = 0
            board_value = BATCH_SIZE
            for value in records:
                flush_counter += 1
                yield board_value == flush_counter, str(value)
                if board_value == flush_counter:
                    flush_counter = 0

        saved_records = 0
        records_to_add: list[str] = []
        async for need_flush, record in iter_over_addresses(addresses):
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
