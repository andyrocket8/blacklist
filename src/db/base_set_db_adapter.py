from abc import ABC
from abc import abstractmethod
from typing import Generic

from src.schemas.abstract_types import K


class SetDbError(Exception):
    pass


class SetDbAdapterError(SetDbError):
    pass


class ISetDbAdapter(ABC, Generic[K]):
    """Interface for sets management"""

    @abstractmethod
    async def add_set(self, set_id: K) -> int:
        pass

    @abstractmethod
    async def del_set(self, set_id: K) -> int:
        pass

    @abstractmethod
    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        pass

    @abstractmethod
    async def exists(self, set_id: K) -> bool:
        pass


class BaseSetDbAdapter(ISetDbAdapter[K], Generic[K]):
    """Wrapper for use without definite DB Adapter (for further dependency injection)"""

    def __init__(self, storage: ISetDbAdapter[K]):
        self.__storage: ISetDbAdapter[K] = storage

    async def add_set(self, set_id: K) -> int:
        return await self.__storage.add_set(set_id)

    async def del_set(self, set_id: K) -> int:
        return await self.__storage.del_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return await self.__storage.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return await self.__storage.exists(set_id)
