from abc import ABC
from typing import Generic

from src.db.base_set_db import ISetDb
from src.db.base_set_db import SetDbError
from src.schemas.abstract_types import K


class SetDbAdapterError(SetDbError):
    pass


class ISetDbAdapter(ISetDb[K], ABC, Generic[K]):
    """Adapter type for Set DB"""

    pass


class BaseSetDbAdapter(ISetDbAdapter[K], Generic[K]):
    """Wrapper for use without definite DB Adapter (for further dependency injection)"""

    def __init__(self, storage: ISetDbAdapter[K]):
        self.__storage: ISetDbAdapter[K] = storage

    async def del_set(self, set_id: K) -> int:
        return await self.__storage.del_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return await self.__storage.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return await self.__storage.exists(set_id)
