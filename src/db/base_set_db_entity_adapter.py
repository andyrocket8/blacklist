from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Type

from src.models.transformation import Transformation
from src.schemas.abstract_types import K
from src.schemas.abstract_types import KInternal
from src.schemas.abstract_types import V
from src.schemas.abstract_types import VInternal

from .base_set_db_entity import ISetDbEntity


class ISetDbEntityAdapter(ISetDbEntity[K, V], Generic[K, V, KInternal, VInternal]):
    """Wrapper for DB Entity Adapter"""

    key_transformer: Type[Transformation[K, KInternal]]
    value_transformer: Type[Transformation[V, VInternal]]

    def __init__(self, set_db_entity_adapter: ISetDbEntity[KInternal, VInternal]):
        self.__set_db_entity_a = set_db_entity_adapter

    async def add_to_set(self, set_id: K, added_data: Iterable[V]) -> int:
        """Add data to set"""
        return await self.__set_db_entity_a.add_to_set(
            self.key_transformer.transform_to_storage(set_id),
            map(self.value_transformer.transform_to_storage, added_data),
        )

    async def del_from_set(self, set_id: K, deleted_data: Iterable[V]) -> int:
        """Remove data from set"""
        return await self.__set_db_entity_a.del_from_set(
            self.key_transformer.transform_to_storage(set_id),
            map(self.value_transformer.transform_to_storage, deleted_data),
        )

    async def fetch_records(self, set_id: K) -> AsyncGenerator[V, None]:
        """Fetch data from set"""
        async for value in self.__set_db_entity_a.fetch_records(self.key_transformer.transform_to_storage(set_id)):
            yield self.value_transformer.transform_from_storage(value)

    async def count(self, set_id: K) -> int:
        """Get records count from set"""
        return await self.__set_db_entity_a.count(self.key_transformer.transform_to_storage(set_id))

    async def contains(self, set_id: K, value: V) -> bool:
        """Check whether set contains value from set"""
        return await self.__set_db_entity_a.contains(
            self.key_transformer.transform_to_storage(set_id), self.value_transformer.transform_to_storage(value)
        )


class BaseSetDbEntityStrAdapter(ISetDbEntityAdapter[K, V, str, str], Generic[K, V]):
    """Base Entity for storages with str keys and str values"""

    pass
