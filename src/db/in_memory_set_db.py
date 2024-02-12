from asyncio import sleep
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable

from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .abstract_set_db import AbstractSetDB
from .abstract_set_db import AbstractUnionSetDB


class InMemorySetDB(AbstractSetDB[K, V], Generic[K, V]):
    """
    InMemory DB Storage with Sets.
    !!! Attention. This DB Storage is for testing purposes only. Do not use in any other cases.

    For use with UUIDs as set IDs and IP addresses as values instantiate as
    obj = InMemorySetDB[UUID, IpV4Address]
    """

    def __init__(self):
        # initialize internal set storage
        self.__data: dict[K, set[V]] = {}

    def get_set(self, set_id: K, create_on_empty: bool = False) -> set[V]:
        """Get set from storage, create if not exists (on create_on_empty == True)"""
        if set_id not in self.__data:
            empty_set: set[V] = set()
            if create_on_empty:
                self.__data[set_id] = empty_set
            return empty_set
        return self.__data[set_id]

    async def remove_set(self, set_id: K):
        """Remove set from storage"""
        if set_id in self.__data:
            del self.__data[set_id]

    async def write_to_set(self, set_id: K, changed_data: Iterable[V]) -> int:
        set_data = self.get_set(set_id, create_on_empty=True)
        records_count = 0
        for elem in changed_data:
            if elem not in set_data:
                set_data.add(elem)
                records_count += 1
                await sleep(0)
        return records_count

    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        set_data = self.get_set(set_id)
        records_count = 0
        for elem in deleted_data:
            if elem in set_data:
                set_data.remove(elem)
                records_count += 1
                await sleep(0)
        if len(set_data) == 0:
            await self.remove_set(set_id)
        return records_count

    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        set_data = self.get_set(set_id)
        for elem in set_data:
            yield elem
            await sleep(0)

    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        return len(self.__data[set_id]) if set_id in self.__data else 0

    async def contains(self, set_id: K, value: V) -> bool:
        """Check whether value is in set"""
        set_data = self.get_set(set_id)
        return value in set_data


class InMemoryUnionSetDB(InMemorySetDB[K, V], AbstractUnionSetDB[K, V], Generic[K, V]):
    """Extend with Union Set functionality"""

    async def fetch_union_records(self, set_id: K, *set_ids_to_union: K) -> AsyncGenerator[V, None]:
        set_data = self.get_set(set_id)
        for union_set_id in set_ids_to_union:
            # need some merge operation
            set_data = set_data.union(self.get_set(union_set_id))
            await sleep(0)
        for elem in set_data:
            yield elem
