from abc import ABC
from abc import abstractmethod
from typing import Generic

from src.schemas.abstract_types import K


class SetDbError(Exception):
    pass


class ISetDb(ABC, Generic[K]):
    """Interface for sets management"""

    @abstractmethod
    async def del_set(self, set_id: K) -> int:
        pass

    @abstractmethod
    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        pass

    @abstractmethod
    async def exists(self, set_id: K) -> bool:
        pass

    @abstractmethod
    async def set_ttl(self, set_id: K, timeout: int):
        """Set TTL for specified set. After timeout expiration it will be eliminated"""
        pass
