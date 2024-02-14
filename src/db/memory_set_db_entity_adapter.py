import logging
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable

from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .base_set_db_entity import ISetDbEntity
from .memory_set_storage import MemorySetStorage


class MemorySetDbEntityAdapter(ISetDbEntity[K, V], Generic[K, V]):
    """Adapter for interaction with MemoryStorage"""

    def __init__(self, storage: MemorySetStorage[K, V]):
        self.__storage = storage

    async def add_to_set(self, set_id: K, added_data: Iterable[V]) -> int:
        """Add data to set"""
        changed_data_t = tuple(x for x in added_data)
        logging.debug('Saving %d records to Memory database, set ID: %s', len(changed_data_t), set_id)
        return await self.__storage.write_to_set(set_id, changed_data_t)

    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        """Remove data from Redis Set"""
        deleted_data_t = tuple(x for x in deleted_data)
        logging.debug('Deleting %d records from Memory database, set ID: %s', len(deleted_data_t), set_id)
        return await self.__storage.del_from_set(set_id, deleted_data_t)

    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        """Fetch data from set"""
        async for record in self.__storage.fetch_records(set_id):
            yield record

    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        logging.debug('Counting records in Memory database, set ID: %s', set_id)
        return self.__storage.count(set_id)

    async def contains(self, set_id: K, value: V) -> bool:
        """Check whether set contains value from set"""
        return self.__storage.contains(set_id, value)
