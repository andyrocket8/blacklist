from typing import Generic
from typing import Iterable
from typing import Type

from src.db.base_union_set_db import IUnionSetDb
from src.models.transformation import Transformation
from src.schemas.abstract_types import K
from src.schemas.abstract_types import KInternal


class BaseUnionSetDbTransformAdapter(IUnionSetDb[K], Generic[K, KInternal]):
    """Class for adopt union operations with transformation to internal storage format"""

    key_transformer: Type[Transformation[K, KInternal]]

    def __init__(self, set_db_adapter: IUnionSetDb[KInternal]):
        self.__union_set_db_adapter: IUnionSetDb[KInternal] = set_db_adapter

    async def union_set(self, set_identities: Iterable[K]) -> K:
        """Union sets and return new set identity. Call to super class with transformation"""
        return self.key_transformer.transform_from_storage(
            await self.__union_set_db_adapter.union_set(map(self.key_transformer.transform_to_storage, set_identities))
        )
