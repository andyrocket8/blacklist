from abc import ABC
from datetime import datetime as dt_datetime
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
from src.schemas.abstract_types import Internal
from src.schemas.abstract_types import T


class IStreamDbAdapter(IStreamDb[SK, IK, T], ABC):
    """Base interface class for all stream adapters"""

    pass


class BaseStreamDbAdapter(IStreamDbAdapter[SK, IK, T], Generic[SK, IK, T, SKInternal, IKInternal, Internal]):
    """Stream DB Adapter for storing without conversion to dict"""

    stream_key_transformer: Type[Transformation[SK, SKInternal]]  # transformer for streams
    ts_transformer: Type[Transformation[IK, IKInternal]]  # transformer for timestamp identity
    value_transformer: Type[Transformation[T, Internal]]  # transformer for value

    def __init__(self, stream_db_adapter: IStreamDb[SKInternal, IKInternal, Internal]):
        self.__stream_db_a = stream_db_adapter

    async def save(self, stream_id: SK, value: T, timestamp_id: Optional[IK] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_a.save(
                self.stream_key_transformer.transform_to_storage(stream_id),
                self.value_transformer.transform_to_storage(value),
                timestamp_id=self.ts_transformer.transform_to_storage(timestamp_id) if timestamp_id else None,
            )
        )

    async def save_by_timestamp(self, stream_id: SK, value: T, timestamp: Optional[dt_datetime] = None) -> IK:
        return self.ts_transformer.transform_from_storage(
            await self.__stream_db_a.save_by_timestamp(
                self.stream_key_transformer.transform_to_storage(stream_id),
                self.value_transformer.transform_to_storage(value),
                timestamp,
            )
        )

    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        return await self.__stream_db_a.delete(
            self.stream_key_transformer.transform_to_storage(stream_id),
            map(self.ts_transformer.transform_to_storage, ids),
        )

    async def read(self, stream_id: SK, timestamp_id: IK) -> Optional[T]:
        value = await self.__stream_db_a.read(
            self.stream_key_transformer.transform_to_storage(stream_id),
            self.ts_transformer.transform_to_storage(timestamp_id),
        )
        return self.value_transformer.transform_from_storage(value) if value is not None else None

    async def fetch_records(
        self, stream_id: SK, start_ts: Optional[dt_datetime] = None, end_ts: Optional[dt_datetime] = None
    ) -> AsyncGenerator[tuple[IK, T], None]:
        async for record in self.__stream_db_a.fetch_records(
            self.stream_key_transformer.transform_to_storage(stream_id), start_ts, end_ts
        ):
            yield self.ts_transformer.transform_from_storage(record[0]), self.value_transformer.transform_from_storage(
                record[1]
            )

    async def count(self, stream_id: SK) -> int:
        """Counting the size of stream"""
        return await self.__stream_db_a.count(self.stream_key_transformer.transform_to_storage(stream_id))
