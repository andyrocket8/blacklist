from typing import Generic

from src.schemas.abstract_types import K

from .base_set_db_adapter import ISetDbAdapter


class BaseSetDb(ISetDbAdapter[K], Generic[K]):
    """Base Set for interaction with DB Adapters"""

    def __init__(self, set_db_adapter: ISetDbAdapter[K]):
        self.__set_db_adapter = set_db_adapter

    async def add_set(self, set_id: K) -> int:
        return await self.__set_db_adapter.add_set(set_id)

    async def del_set(self, set_id: K) -> int:
        return await self.__set_db_adapter.del_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return await self.__set_db_adapter.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return await self.__set_db_adapter.exists(set_id)
