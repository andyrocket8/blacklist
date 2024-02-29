from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import AsyncGenerator
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import Optional

from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IStreamDb
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V
from src.utils.time_utils import get_epoch_time


@dataclass
class MemoryStorageItem(Generic[IK, K, V]):
    timestamp: IK
    values: dict[K, V] = field(default_factory=dict)


class MemoryStreamStorage(IStreamDb[SK, IK, K, V], Generic[SK, IK, K, V]):
    timestamp_factory: Callable[[], IK]
    timestamp_generator: Callable[[int], IK]  # Should generate unique ID from timestamp

    def __init__(self):
        self.__storage: dict[SK, list[MemoryStorageItem]] = defaultdict(list)

    async def save(self, stream_id: SK, values: dict[K, V], timestamp_id: Optional[IK]) -> IK:
        """Save by timestamp key (add and possibly update)"""
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        if timestamp_id is not None:
            for value in stream_data:
                if value.timestamp == timestamp_id:
                    value.values |= values
                    break
            else:
                # no data has been found
                stream_data.append(MemoryStorageItem(timestamp_id, values))
        else:
            timestamp_id = self.timestamp_factory()
            stream_data.append(MemoryStorageItem(timestamp_id, values))
        return timestamp_id

    async def save_by_timestamp(self, stream_id: SK, values: dict[K, V], timestamp: Optional[int] = None) -> IK:
        """Save by timestamp value
        Form unique key on save (always add)
        """
        if timestamp is not None:
            timestamp_id: IK = self.timestamp_generator(timestamp)
        else:
            timestamp_id = self.timestamp_factory()
        return await self.save(stream_id, values, timestamp_id)

    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        deleted_count = 0
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        for timestamp_id in ids:
            for item in stream_data:
                if timestamp_id == item.timestamp:
                    stream_data.remove(item)
                    deleted_count += 1
                    break
        return deleted_count

    async def read(self, stream_id: SK, timestamp_id: IK) -> dict[K, V]:
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        for item in stream_data:
            if timestamp_id == item.timestamp:
                return item.values
        return dict()

    async def fetch_records(
        self, stream_id: SK, start_ts: int, end_ts: Optional[int] = None
    ) -> AsyncGenerator[tuple[IK, dict[K, V]], None]:
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        for item in sorted(stream_data, key=lambda x: x.timestamp):
            yield item.timestamp, item.values


class MemoryStreamTsStorage(MemoryStreamStorage[SK, str, K, V], Generic[SK, K, V]):
    """Storage with timestamp like in redis storage (epoch in millis with unique counter)"""

    def __init__(self):
        super().__init__()
        self.__unique_counter = 0
        self.timestamp_factory = self.timestamp_str_factory
        self.timestamp_generator = self.timestamp_str_generator

    def gen_counter(self) -> str:
        self.__unique_counter += 1
        return ('000000' + str(self.__unique_counter))[:-6]

    def timestamp_str_factory(self) -> str:
        return f'{get_epoch_time()}-{self.gen_counter()}'

    def timestamp_str_generator(self, timestamp: int) -> str:
        return f'{timestamp}-{self.gen_counter()}'
