# Abstract DB connector
import asyncio
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable

from src.models.abstract_types import K
from src.models.abstract_types import T


class AbstractSetDbError(Exception):
    pass


class AbstractDBSet(ABC, Generic[K, T]):
    """Abstract DB Connector with Set Features implementation"""

    @abstractmethod
    async def write_set(self, set_id: K, changed_data: Iterable[T]) -> int:
        """Write data to set. Create set if not exists
        :returns int: count of affected records
        """
        pass

    @abstractmethod
    async def del_set(self, set_id: K, deleted_data: Iterable[T]) -> int:
        """Delete data from set. If set remains empty - remove empty set
        :returns int: count of affected records
        """
        pass

    @abstractmethod
    async def fetch_records(self, set_id: K, *set_ids_to_union: K) -> AsyncGenerator[Any, None]:
        """Fetch records from set. If needed union operation before fetch - pass set identifiers in optional params"""
        # Emulate async generator behaviour in abstract method
        await asyncio.sleep(0)  # calling awaitable
        yield None  # yield result

    @abstractmethod
    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        pass
