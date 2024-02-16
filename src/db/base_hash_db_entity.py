from abc import ABC
from abc import abstractmethod
from asyncio import sleep as a_sleep
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional
from typing import cast

from src.schemas.abstract_types import H
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V


class IHashDbEntity(ABC, Generic[H, K, V]):
    """Interface for working with Typed Hash storages"""

    @abstractmethod
    async def write_values(self, hash_id: H, items: Iterable[tuple[K, V]]) -> int:
        """Write data to hash storage"""
        pass

    @abstractmethod
    async def delete_values(self, hash_id: H, items_keys: Iterable[K]) -> int:
        """Delete data from hash storage"""
        pass

    @abstractmethod
    async def read_value(self, hash_id: H, key: K) -> Optional[V]:
        """Read data from hash storage"""
        pass

    @abstractmethod
    async def fetch_records(self, hash_id: H) -> AsyncGenerator[tuple[K, V], None]:
        """Read data from hash storage"""
        await a_sleep(0)
        yield cast(tuple[K, V], None)

    @abstractmethod
    async def count(self, hash_id: H) -> int:
        """Returns count for specified hash_id"""
        pass

    @abstractmethod
    async def contains(self, hash_id: H, key: K) -> bool:
        """Returns whether key exists in hash_id"""
        pass
