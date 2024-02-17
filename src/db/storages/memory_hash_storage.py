from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional

from src.schemas.abstract_types import H
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

STORAGE_DATA_ATTR = '_MemoryHashStorage__db'


class MemoryHashStorage(Generic[H, K, V]):
    """Hash memory storage"""

    def __init__(self):
        self.__db: dict[H, dict[K, V]] = dict()

    def __get_hash_storage(self, hash_id: H) -> dict[K, V]:
        return self.__db.get(hash_id, dict())

    def __rm_hash_storage(self, hash_id: H):
        if hash_id in self.__db:
            del self.__db[hash_id]

    async def write_values(self, hash_id: H, items: Iterable[tuple[K, V]]) -> int:
        hash_storage = self.__get_hash_storage(hash_id)
        affected_items = 0
        for key, value in items:
            # check value
            stored_value = hash_storage.get(key)
            if stored_value != value:
                hash_storage[key] = value
                affected_items += 1
        if hash_id not in self.__db:
            # store new storage in internal db
            self.__db[hash_id] = hash_storage
        return affected_items

    async def delete_values(self, hash_id: H, items_keys: Iterable[K]) -> int:
        """Delete data from hash storage"""
        hash_storage = self.__get_hash_storage(hash_id)
        affected_items = 0
        for key in items_keys:
            if key in hash_storage:
                affected_items += 1
                del hash_storage[key]
        if await self.count(hash_id) == 0:
            self.__rm_hash_storage(hash_id)
        return affected_items

    async def read_value(self, hash_id: H, key: K) -> Optional[V]:
        """Read data from hash storage"""
        hash_storage = self.__get_hash_storage(hash_id)
        return hash_storage.get(key)

    async def fetch_records(self, hash_id: H) -> AsyncGenerator[tuple[K, V], None]:
        """Read data from hash storage"""
        hash_storage = self.__get_hash_storage(hash_id)
        for key, value in hash_storage.items():
            yield key, value

    async def count(self, hash_id: H) -> int:
        """Returns count for specified hash_id"""
        return len(self.__get_hash_storage(hash_id))

    async def contains(self, hash_id: H, key: K) -> bool:
        """Returns whether key exists in hash_id"""
        return key in self.__get_hash_storage(hash_id)
