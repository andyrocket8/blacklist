from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional

from src.db.base_hash_db_entity import IHashDbEntity
from src.db.storages.memory_hash_storage import MemoryHashStorage
from src.schemas.abstract_types import H
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V


class MemoryHashDbEntity(IHashDbEntity[H, K, V], Generic[H, K, V]):
    def __init__(self, storage_obj: MemoryHashStorage):
        self.__db = storage_obj

    async def write_values(self, hash_id: H, items: Iterable[tuple[K, V]]) -> int:
        """Write data to hash storage"""
        return await self.__db.write_values(hash_id, items)

    async def delete_values(self, hash_id: H, items_keys: Iterable[K]) -> int:
        """Delete data from hash storage"""
        return await self.__db.delete_values(hash_id, items_keys)

    async def read_value(self, hash_id: H, key: K) -> Optional[V]:
        """Read data from hash storage"""
        return await self.__db.read_value(hash_id, key)

    async def fetch_records(self, hash_id: H) -> AsyncGenerator[tuple[K, V], None]:
        """Read data from hash storage"""
        async for key, value in self.__db.fetch_records(hash_id):
            yield key, value

    async def count(self, hash_id: H) -> int:
        """Returns count for specified hash_id"""
        return await self.__db.count(hash_id)

    async def contains(self, hash_id: H, key: K) -> bool:
        """Returns whether key exists in hash_id"""
        return await self.__db.contains(hash_id, key)
