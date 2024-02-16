from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional
from typing import Type

from src.db.base_hash_db_entity import IHashDbEntity
from src.models.transformation import Transformation
from src.schemas.abstract_types import H
from src.schemas.abstract_types import HInternal
from src.schemas.abstract_types import K
from src.schemas.abstract_types import KInternal
from src.schemas.abstract_types import V
from src.schemas.abstract_types import VInternal


class IHashDbEntityAdapter(IHashDbEntity[H, K, V], Generic[H, K, V, HInternal, KInternal, VInternal]):
    hash_transformer: Type[Transformation[H, HInternal]]
    key_transformer: Type[Transformation[K, KInternal]]
    value_transformer: Type[Transformation[V, VInternal]]

    def __init__(self, hash_db_entity_adapter: IHashDbEntity[HInternal, KInternal, VInternal]):
        self.__hash_db_entity_a = hash_db_entity_adapter

    async def write_values(self, hash_id: H, items: Iterable[tuple[K, V]]) -> int:
        """Write data to hash storage"""
        return await self.__hash_db_entity_a.write_values(
            self.hash_transformer.transform_to_storage(hash_id),
            map(
                lambda record: (
                    self.key_transformer.transform_to_storage(record[0]),
                    self.value_transformer.transform_to_storage(record[1]),
                ),
                items,
            ),
        )

    async def delete_values(self, hash_id: H, items_keys: Iterable[K]) -> int:
        return await self.__hash_db_entity_a.delete_values(
            self.hash_transformer.transform_to_storage(hash_id),
            map(self.key_transformer.transform_to_storage, items_keys),
        )

    async def read_value(self, hash_id: H, key: K) -> Optional[V]:
        """Read data from hash storage"""
        value: Optional[VInternal] = await self.__hash_db_entity_a.read_value(
            self.hash_transformer.transform_to_storage(hash_id), self.key_transformer.transform_to_storage(key)
        )
        return self.value_transformer.transform_from_storage(value) if value is not None else None

    async def fetch_records(self, hash_id: H) -> AsyncGenerator[tuple[K, V], None]:
        """Read data from hash storage"""
        async for key, value in self.__hash_db_entity_a.fetch_records(
            self.hash_transformer.transform_to_storage(hash_id)
        ):
            yield self.key_transformer.transform_from_storage(key), self.value_transformer.transform_from_storage(value)

    async def count(self, hash_id: H) -> int:
        """Returns count for specified hash_id"""
        return await self.__hash_db_entity_a.count(self.hash_transformer.transform_to_storage(hash_id))

    async def contains(self, hash_id: H, key: K) -> bool:
        """Returns whether key exists in hash_id"""
        return await self.__hash_db_entity_a.contains(
            self.hash_transformer.transform_to_storage(hash_id), self.key_transformer.transform_to_storage(key)
        )
