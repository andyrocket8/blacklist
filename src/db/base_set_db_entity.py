# Base abstract classes and interfaces for Set Entities methods e.g. read from set, write to set etc.

from abc import ABC
from abc import abstractmethod
from asyncio import sleep as asleep
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import cast

from src.db.adapters.base_set_db_adapter import SetDbError
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V


class SetDbIdentityError(SetDbError):
    pass


class ISetDbEntity(ABC, Generic[K, V]):
    """Interface for set entity routines (add, delete, fetch)"""

    @abstractmethod
    async def add_to_set(self, set_id: K, added_data: Iterable[V]) -> int:
        """Add data to set"""
        pass

    @abstractmethod
    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        """Remove data from set"""
        pass

    @abstractmethod
    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        """Fetch data from set"""
        await asleep(0)  # calling awaitable
        yield cast(V, None)  # patch for mypy warnings on incompatible type (do not do this in nested implementations)

    @abstractmethod
    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        pass

    @abstractmethod
    async def contains(self, set_id: K, value: V) -> bool:
        """Check whether set contains value from set"""
        pass
