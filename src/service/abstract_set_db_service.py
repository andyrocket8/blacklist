import logging
from typing import AsyncGenerator
from typing import Generic
from typing import Optional
from typing import TypeVar
from uuid import UUID

from src.core.settings import BATCH_SIZE
from src.db.base_set_db_entity import ISetDbEntity
from src.schemas.abstract_types import T


async def iter_over_records(iter_records: list[T]) -> AsyncGenerator[tuple[int, T], None]:
    """Iterate over recordset"""
    flush_counter = 0
    board_value = BATCH_SIZE
    for value in iter_records:
        flush_counter += 1
        yield board_value == flush_counter, value
        if board_value == flush_counter:
            flush_counter = 0


class AbstractSetDBService(Generic[T]):
    """Serve operations with abstract classes in Redis database"""

    class_set_id: UUID

    def __init__(self, db_entity: ISetDbEntity[UUID, T], set_id: Optional[UUID] = None):
        self.__db_entity: ISetDbEntity[UUID, T] = db_entity
        self.__set_id: UUID = set_id if set_id is not None else self.class_set_id

    async def fetch_records(self, records_count: int = 0, all_records: bool = True) -> AsyncGenerator[T, None]:
        current_record = 0
        async for record in self.__db_entity.fetch_records(self.__set_id):
            yield record
            if not all_records and records_count > 0:
                current_record += 1
                if current_record >= records_count:
                    break

    async def get_records(self, records_count: int = 0, all_records: bool = True) -> list[T]:
        """Getting records from database"""
        result = []
        set_id: str = str(self.__set_id)
        logging.debug('Getting records from database, set ID: %s', set_id)
        async for record in self.fetch_records(records_count, all_records):
            result.append(record)
        logging.debug('Retrieved %s records from database, set ID: %s', len(result), set_id)
        return result

    async def write_records(self, records: list[T]) -> int:
        """Saving records to database
        Split data into pieces and write these chunks to Redis DB
        """
        saved_records = 0
        records_to_add: list[T] = []
        async for need_flush, record in iter_over_records(records):
            records_to_add.append(record)
            if need_flush:
                iter_written = await self.__db_entity.add_to_set(self.__set_id, records_to_add)
                saved_records += iter_written
                records_to_add = []
        if len(records_to_add):
            iter_written = await self.__db_entity.add_to_set(self.__set_id, records_to_add)
            saved_records += iter_written
        logging.debug('Actually wrote %d records to database', saved_records)
        return saved_records

    async def del_records(self, records: list[T]) -> int:
        """Delete records from database
        Split data into pieces and delete these chunks from Redis DB
        """
        deleted_records = 0
        records_to_delete: list[T] = []
        async for need_flush, record in iter_over_records(records):
            records_to_delete.append(record)
            if need_flush:
                iter_deleted = await self.__db_entity.del_from_set(self.__set_id, records_to_delete)
                deleted_records += iter_deleted
                records_to_delete = []
        if len(records_to_delete):
            iter_deleted = await self.__db_entity.del_from_set(self.__set_id, records_to_delete)
            deleted_records += iter_deleted
        logging.debug('Total deleted %d records from database', deleted_records)
        return deleted_records

    async def count(self) -> int:
        logging.debug('Counting records in database, set ID: %s')
        return await self.__db_entity.count(self.__set_id)


AbstractSetDBServiceType = TypeVar('AbstractSetDBServiceType', bound=AbstractSetDBService)
