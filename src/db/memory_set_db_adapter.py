from typing import Any
from typing import Generic

from src.db.memory_set_storage import MemorySetStorage
from src.schemas.abstract_types import K

from .base_set_db_adapter import ISetDbAdapter


class MemorySetDbAdapter(ISetDbAdapter[K], Generic[K]):
    """Adapter with ISetDbAdapter interface (without type transformation)"""

    def __init__(self, storage: MemorySetStorage[K, Any]):
        self.__storage: MemorySetStorage[K, Any] = storage

    async def del_set(self, set_id: K) -> int:
        return self.__storage.remove_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return self.__storage.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return self.__storage.exists(set_id)
