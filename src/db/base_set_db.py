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


class BaseSetDb(ISetDb[K], Generic[K]):
    """Base Set for interaction with DB Adapters"""

    def __init__(self, set_db_adapter: ISetDb[K]):
        self.__set_db_adapter = set_db_adapter

    async def del_set(self, set_id: K) -> int:
        return await self.__set_db_adapter.del_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return await self.__set_db_adapter.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return await self.__set_db_adapter.exists(set_id)
