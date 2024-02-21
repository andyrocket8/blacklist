from typing import Any
from typing import Callable
from typing import Iterable

from src.db.base_union_set_db import IUnionSetDb
from src.db.storages.memory_set_storage import MemorySetStorage
from src.schemas.abstract_types import K


class MemoryUnionSetDbAdapter(IUnionSetDb[K]):
    def __init__(self, storage: MemorySetStorage[K, Any], key_generator: Callable[[], K]):
        self.__storage = storage
        self.__key_generator = key_generator

    async def union_set(self, set_identities: Iterable[K]) -> K:
        new_set_id: K = self.__key_generator()
        self.__storage.union_sets(new_set_id, set_identities)
        return new_set_id
