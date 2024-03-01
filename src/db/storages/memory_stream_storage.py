from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime as dt_datetime
from typing import AsyncGenerator
from typing import Callable
from typing import Generic
from typing import Iterable
from typing import Optional

from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IStreamDb
from src.schemas.abstract_types import T
from src.utils.time_utils import get_current_epoch_time
from src.utils.time_utils import get_epoch_time


@dataclass
class MemoryStorageItem(Generic[IK, T]):
    timestamp: IK
    value: T


class MemoryStreamStorage(IStreamDb[SK, IK, T], Generic[SK, IK, T]):

    timestamp_factory: Callable[[], IK]
    timestamp_generator: Callable[[dt_datetime], IK]  # Should generate unique ID from timestamp
    to_datetime_converter: Callable[[IK], dt_datetime]

    def __init__(self):
        self.__storage: dict[SK, list[MemoryStorageItem]] = defaultdict(list)

    async def save(self, stream_id: SK, new_value: T, timestamp_id: Optional[IK]) -> IK:
        """Save by timestamp key (add and possibly update)"""
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        if timestamp_id is not None:
            for item in stream_data:
                if item.timestamp == timestamp_id:
                    item.value = new_value
                    break
            else:
                # no data has been found
                stream_data.append(MemoryStorageItem(timestamp_id, new_value))
        else:
            timestamp_id = self.timestamp_factory()
            stream_data.append(MemoryStorageItem(timestamp_id, new_value))
        return timestamp_id

    async def save_by_timestamp(self, stream_id: SK, value: T, timestamp: Optional[dt_datetime] = None) -> IK:
        """Save by timestamp value
        Form unique key on save (always add)
        """
        if timestamp is not None:
            timestamp_id: IK = self.timestamp_generator(timestamp)
        else:
            timestamp_id = self.timestamp_factory()
        return await self.save(stream_id, value, timestamp_id)

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

    async def read(self, stream_id: SK, timestamp_id: IK) -> Optional[T]:
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id]
        for item in stream_data:
            if timestamp_id == item.timestamp:
                return item.value
        return None

    async def fetch_records(
        self, stream_id: SK, start_ts: Optional[dt_datetime] = None, end_ts: Optional[dt_datetime] = None
    ) -> AsyncGenerator[tuple[IK, T], None]:
        stream_data: list[MemoryStorageItem] = self.__storage[stream_id].copy()  # make persistent copy
        for item in sorted(stream_data, key=lambda x: x.timestamp):
            current_record_datetime = self.to_datetime_converter(item.timestamp)
            if end_ts is not None and current_record_datetime > end_ts:
                # end iteration by stop date time
                break
            if start_ts is None or current_record_datetime >= start_ts:
                # yield if we are in time range
                yield item.timestamp, item.value


class MemoryStreamTsStorage(MemoryStreamStorage[SK, str, T], Generic[SK, T]):
    """Storage with timestamp likely in redis storage (epoch in millis with unique counter)"""

    def __init__(self):
        super().__init__()
        self.__unique_counter = 0
        self.timestamp_factory = self.timestamp_str_factory
        self.timestamp_generator = self.timestamp_str_generator
        self.to_datetime_converter = self.datetime_from_ts_str

    def gen_counter(self) -> str:
        self.__unique_counter += 1
        return ('00000000' + str(self.__unique_counter))[-8:]

    def timestamp_str_factory(self) -> str:
        return f'{get_current_epoch_time()}-{self.gen_counter()}'

    def timestamp_str_generator(self, timestamp: dt_datetime) -> str:
        return f'{get_epoch_time(timestamp)}-{self.gen_counter()}'

    def datetime_from_ts_str(self, timestamp: str) -> dt_datetime:
        return dt_datetime.fromtimestamp(int(timestamp[:-9]) / 1000)
