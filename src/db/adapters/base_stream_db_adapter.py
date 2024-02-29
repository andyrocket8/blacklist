from abc import ABC
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional
from typing import Type

from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IKInternal
from src.db.base_stream_db import IStreamDb
from src.db.base_stream_db import SKInternal
from src.models.transformation import Transformation
from src.schemas.abstract_types import K
from src.schemas.abstract_types import KInternal
from src.schemas.abstract_types import T
from src.schemas.abstract_types import V
from src.schemas.abstract_types import VInternal


class IStreamDbAdapter(IStreamDb[SK, IK, K, V], ABC):
    """Base interface class for all stream adapters"""

    pass


class BaseStreamDbAdapter(
    IStreamDbAdapter[SK, IK, K, V], Generic[SK, IK, K, V, SKInternal, IKInternal, KInternal, VInternal]
):
    """Wrapper for DB Entity Adapter"""

    stream_key_transformer: Type[Transformation[SK, SKInternal]]  # transformer for streams
    ts_transformer: Type[Transformation[IK, IKInternal]]  # transformer for timestamp identity
    key_transformer: Type[Transformation[K, KInternal]]  # transformer for key
    value_transformer: Type[Transformation[V, VInternal]]  # transformer for value

    def __init__(self, stream_db_adapter: IStreamDb[SKInternal, IKInternal, KInternal, VInternal]):
        self.__stream_db_a = stream_db_adapter

    async def save(self, stream_id: SK, values: dict[K, V], timestamp_id: Optional[IK] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_a.save(
                self.stream_key_transformer.transform_to_storage(stream_id),
                {
                    self.key_transformer.transform_to_storage(k): self.value_transformer.transform_to_storage(v)
                    for k, v in values.items()
                },
                timestamp_id=self.ts_transformer.transform_to_storage(timestamp_id) if timestamp_id else None,
            )
        )

    async def save_by_timestamp(self, stream_id: SK, values: dict[K, V], timestamp: Optional[int] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_a.save_by_timestamp(
                self.stream_key_transformer.transform_to_storage(stream_id),
                {
                    self.key_transformer.transform_to_storage(k): self.value_transformer.transform_to_storage(v)
                    for k, v in values.items()
                },
                timestamp,
            )
        )

    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        return await self.__stream_db_a.delete(
            self.stream_key_transformer.transform_to_storage(stream_id),
            map(self.ts_transformer.transform_to_storage, ids),
        )

    async def read(self, stream_id: SK, timestamp_id: IK) -> dict[K, V]:
        return {
            self.key_transformer.transform_from_storage(k): self.value_transformer.transform_from_storage(v)
            for k, v in (
                await self.__stream_db_a.read(
                    self.stream_key_transformer.transform_to_storage(stream_id),
                    self.ts_transformer.transform_to_storage(timestamp_id),
                )
            ).items()
        }

    async def fetch_records(
        self, stream_id: SK, start_ts: int, end_ts: Optional[int] = None
    ) -> AsyncGenerator[tuple[IK, dict[K, V]], None]:
        async for record in self.__stream_db_a.fetch_records(
            self.stream_key_transformer.transform_to_storage(stream_id), start_ts, end_ts
        ):
            yield self.ts_transformer.transform_from_storage(record[0]), {
                self.key_transformer.transform_from_storage(k): self.value_transformer.transform_from_storage(v)
                for k, v in record[1].items()
            }


class BaseEntityStreamAdapter(
    Generic[SK, IK, T, SKInternal, IKInternal, KInternal, VInternal],
):
    """Stream Adapter for storing Entities as dicts"""

    stream_key_transformer: Type[Transformation[SK, SKInternal]]  # transformer for streams
    ts_transformer: Type[Transformation[IK, IKInternal]]
    entity_transformer: Transformation[T, dict[KInternal, VInternal]]

    def __init__(self, stream_db_adapter: IStreamDb[SKInternal, IKInternal, KInternal, VInternal]):
        self.__stream_db_adapter = stream_db_adapter

    async def save(self, stream_id: SK, value: T, timestamp_id: Optional[IK] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_adapter.save(
                self.stream_key_transformer.transform_to_storage(stream_id),
                self.entity_transformer.transform_to_storage(value),
                timestamp_id=(
                    self.ts_transformer.transform_to_storage(timestamp_id) if timestamp_id is not None else None
                ),
            )
        )

    async def save_by_timestamp(self, stream_id: SK, value: T, timestamp: Optional[int] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_adapter.save_by_timestamp(
                self.stream_key_transformer.transform_to_storage(stream_id),
                self.entity_transformer.transform_to_storage(value),
                timestamp,
            )
        )

    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        return await self.__stream_db_adapter.delete(
            self.stream_key_transformer.transform_to_storage(stream_id),
            map(self.ts_transformer.transform_to_storage, ids),
        )

    async def read(self, stream_id: SK, timestamp_id: IK) -> Optional[T]:
        values: dict[KInternal, VInternal] = await self.__stream_db_adapter.read(
            self.stream_key_transformer.transform_to_storage(stream_id),
            self.ts_transformer.transform_to_storage(timestamp_id),
        )
        return self.entity_transformer.transform_from_storage(values) if values else None

    async def fetch_records(
        self, stream_id: SK, start_ts: int, end_ts: Optional[int] = None
    ) -> AsyncGenerator[tuple[IK, T], None]:
        async for record in self.__stream_db_adapter.fetch_records(
            self.stream_key_transformer.transform_to_storage(stream_id), start_ts, end_ts
        ):
            yield self.ts_transformer.transform_from_storage(record[0]), self.entity_transformer.transform_from_storage(
                record[1]
            )
