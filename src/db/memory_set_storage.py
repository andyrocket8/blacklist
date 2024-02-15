from asyncio import sleep as asleep
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable

from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .base_set_db_adapter import ISetDbAdapter
from .base_set_db_entity import ISetDbEntity


class MemorySetStorage(Generic[K, V]):
    """Storage for handling sets in memory aka DB storage
    Methods are not the same as ISet...Adapters!
    """

    def __init__(self):
        # initialize internal set storage
        self.__data: dict[K, set[V]] = {}

    def __add_set(self, set_id: K):
        """Internal function for set addition"""
        if set_id not in self.__data:
            self.__data[set_id] = set()

    def get_set(self, set_id: K) -> set[V]:
        """Get set from storage, create if not exists (default behaviour for redis)"""
        if set_id not in self.__data:
            self.__add_set(set_id)
        return self.__data[set_id]

    def remove_set(self, set_id: K) -> int:
        """Remove set from storage (with data elimination)"""
        if set_id in self.__data:
            del self.__data[set_id]
            return 1
        return 0

    def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        if source_set_id in self.__data:
            # we have something to copy
            if target_set_id not in self.__data or with_replace:
                self.__data[target_set_id] = self.__data[source_set_id].copy()
                return 1
        return 0

    def exists(self, set_id: K) -> bool:
        return set_id in self.__data

    async def write_to_set(self, set_id: K, changed_data: Iterable[V]) -> int:
        set_data = self.get_set(set_id)
        records_count = 0
        for elem in changed_data:
            if elem not in set_data:
                set_data.add(elem)
                records_count += 1
                await asleep(0)
        return records_count

    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        set_data = self.get_set(set_id)
        records_count = 0
        for elem in deleted_data:
            if elem in set_data:
                set_data.remove(elem)
                records_count += 1
                await asleep(0)
        return records_count

    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        set_data = self.get_set(set_id)
        for elem in set_data:
            yield elem
            await asleep(0)

    def count(self, set_id: K) -> int:
        """Get records count from set"""
        return len(self.__data[set_id]) if set_id in self.__data else 0

    def contains(self, set_id: K, value: V) -> bool:
        """Check whether value is in set"""
        set_data = self.get_set(set_id)
        return value in set_data

    def set_db_adapter(self) -> ISetDbAdapter[K]:
        from .memory_set_db_adapter import MemorySetDbAdapter

        return MemorySetDbAdapter(self)

    def set_db_entity_adapter(self) -> ISetDbEntity[K, V]:
        from .memory_set_db_entity_adapter import MemorySetDbEntityAdapter

        return MemorySetDbEntityAdapter[K, V](self)