# Abstract DB connector
import asyncio
from abc import ABC
from abc import abstractmethod
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import cast

from src.schemas.abstract_types import K
from src.schemas.abstract_types import V


class AbstractSetDBError(Exception):
    pass


class AbstractSetDB(ABC, Generic[K, V]):
    """Abstract DB Connector with Set Features implementation
    Assume that set is created on first write operation
    """

    @abstractmethod
    async def write_to_set(self, set_id: K, changed_data: Iterable[V]) -> int:
        """Write data to set. Create set if not exists
        :returns int: count of affected records
        """
        pass

    @abstractmethod
    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        """Delete data from set. If set remains empty - remove empty set
        :returns int: count of affected records
        """
        pass

    @abstractmethod
    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        """Fetch records from set."""
        # Emulate async generator behaviour in abstract method
        await asyncio.sleep(0)  # calling awaitable
        yield cast(V, None)  # yield result

    @abstractmethod
    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        pass

    @abstractmethod
    async def remove_set(self, set_id: K):
        """Remove set from DB"""
        pass

    @abstractmethod
    async def contains(self, set_id: K, value: V) -> bool:
        """Check whether value is in set"""
        pass


class AbstractUnionSetInterface(ABC, Generic[K, V]):
    """Interface with union read operations"""

    @abstractmethod
    async def fetch_union_records(self, set_id: K, *set_ids_to_union: K) -> AsyncGenerator[V, None]:
        """
        Fetch records from set or union of sets.
        If needed union operation before fetch - pass set identifiers in optional params
        """
        # Emulate async generator behaviour in abstract method
        await asyncio.sleep(0)  # calling awaitable
        yield cast(V, None)  # patch for mypy warnings on incompatible type (do not do this in nested implementations)


class AbstractUnionSetDB(AbstractSetDB[K, V], AbstractUnionSetInterface[K, V], ABC, Generic[K, V]):
    """Composite class with union feature"""

    pass
