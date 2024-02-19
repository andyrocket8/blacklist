from abc import ABC
from typing import Generic
from typing import Type

from src.db.base_set_db import ISetDb
from src.db.base_set_db import SetDbError
from src.models.transformation import Transformation
from src.schemas.abstract_types import K
from src.schemas.abstract_types import KInternal


class SetDbAdapterError(SetDbError):
    pass


class ISetDbAdapter(ISetDb[K], ABC, Generic[K]):
    """Adapter type for Set DB"""

    pass


class BaseSetDbAdapter(ISetDbAdapter[K], Generic[K, KInternal]):
    """Wrapper for use without definite DB Adapter (for further dependency injection)"""

    key_transform: Type[Transformation[K, KInternal]]

    def __init__(self, storage: ISetDbAdapter[KInternal]):
        self.__storage: ISetDbAdapter[KInternal] = storage

    async def del_set(self, set_id: K) -> int:
        return await self.__storage.del_set(self.key_transform.transform_to_storage(set_id))

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return await self.__storage.copy_set(
            self.key_transform.transform_to_storage(source_set_id),
            self.key_transform.transform_to_storage(target_set_id),
            with_replace,
        )

    async def exists(self, set_id: K) -> bool:
        return await self.__storage.exists(self.key_transform.transform_to_storage(set_id))
