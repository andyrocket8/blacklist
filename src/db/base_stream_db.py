# Interface to work with streams
from abc import ABC
from abc import abstractmethod
from datetime import datetime as dt_datetime
from typing import AsyncGenerator
from typing import Generic
from typing import Iterable
from typing import Optional
from typing import TypeVar
from typing import cast

from src.schemas.abstract_types import K
from src.schemas.abstract_types import T
from src.schemas.abstract_types import V

# Key value for stream
SK = TypeVar('SK')
# Key value for stream (Internal storage of adapter)
SKInternal = TypeVar('SKInternal')


# Timestamp key for stream (id)
IK = TypeVar('IK')
# Timestamp key for stream (id), internal type for storage adapter
IKInternal = TypeVar('IKInternal')


class IStreamDbError(Exception):
    pass


class IStreamDb(ABC, Generic[SK, IK, T]):
    """Abstract interface to operate with streams
    SK are key values for streams (time-series storages)
    IK are timestamp based keys
    T is an entity to store in stream

    timestamps operated in this interface are UNIX epoch values in milliseconds
    """

    @abstractmethod
    async def save(self, stream_id: SK, value: T, timestamp_id: Optional[IK]) -> IK:
        """Save by timestamp key (add and possibly update)"""
        pass

    @abstractmethod
    async def save_by_timestamp(self, stream_id: SK, value: T, timestamp: Optional[dt_datetime] = None) -> IK:
        """Save by timestamp value
        Form unique key on save (always add)
        """
        pass

    @abstractmethod
    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        """Deleting series of keys"""
        pass

    @abstractmethod
    async def read(self, stream_id: SK, timestamp_id: IK) -> Optional[T]:
        """Reading one record"""
        pass

    @abstractmethod
    async def fetch_records(
        self, stream_id: SK, start_ts: Optional[dt_datetime] = None, end_ts: Optional[dt_datetime] = None
    ) -> AsyncGenerator[tuple[IK, T], None]:
        """Generator for fetching data from stream"""
        yield cast(IK, None), cast(T, None)  # monkeypatching for linter error suppressing


class IDictStreamDb(ABC, Generic[SK, IK, K, V]):
    """Abstract interface to operate with streams
    SK are key values for streams (time-series storages)
    IK are timestamp based keys
    K is key for dict
    V is value for dict

    timestamps operated in this interface are UNIX epoch values in milliseconds
    """

    @abstractmethod
    async def save(self, stream_id: SK, values: dict[K, V], timestamp_id: Optional[IK]) -> IK:
        """Save by timestamp key (add and possibly update)"""
        pass

    @abstractmethod
    async def save_by_timestamp(self, stream_id: SK, values: dict[K, V], timestamp: Optional[dt_datetime] = None) -> IK:
        """Save by timestamp value
        Form unique key on save (always add)
        """
        pass

    @abstractmethod
    async def delete(self, stream_id: SK, ids: Iterable[IK]) -> int:
        """Deleting series of keys"""
        pass

    @abstractmethod
    async def read(self, stream_id: SK, timestamp_id: IK) -> Optional[dict[K, V]]:
        """Reading one record"""
        pass

    @abstractmethod
    async def fetch_records(
        self, _stream_id: SK, _start_ts: Optional[dt_datetime] = None, _end_ts: Optional[dt_datetime] = None
    ) -> AsyncGenerator[tuple[IK, dict[K, V]], None]:
        """Generator for fetching data from stream"""
        yield cast(IK, None), dict()  # monkeypatching for linter error suppressing
