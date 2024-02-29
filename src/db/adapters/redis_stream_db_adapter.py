import logging
from typing import AsyncGenerator
from typing import Iterable
from typing import Optional
from typing import cast

from redis.asyncio import Redis as RedisAsyncio
from redis.asyncio import RedisError

from src.core.settings import MAX_BUNDLE_SIZE
from src.db.base_stream_db import IStreamDbError

from .base_stream_db_adapter import IStreamDbAdapter


class RedisStreamDbAdapter(IStreamDbAdapter[str, str, str, bytes]):
    """Adapter for redis storing keys as str, values as bytes
    Timestamp values are stored in str, transformed to str from unix epoch with suffix if unique int
    """

    def __init__(self, db: RedisAsyncio, max_bundle_size=MAX_BUNDLE_SIZE):
        self.__db = db
        self.__max_bundle_size = max_bundle_size

    async def save(self, stream_id: str, values: dict[str, bytes], timestamp_id: Optional[str] = None) -> str:
        try:
            return await self.__db.xadd(
                stream_id,
                # some mypy lint error patching here
                cast(dict[bytes | memoryview | str | int | float, bytes | memoryview | str | int | float], values),
                minid=timestamp_id,
            )
        except RedisError as e:
            logging.error(f'Error while saving stream data, stream ID: {stream_id}, details: {str(e)}')
            raise IStreamDbError from None

    async def save_by_timestamp(self, stream_id: str, values: dict[str, bytes], timestamp: Optional[int] = None) -> str:
        try:
            return await self.__db.xadd(
                stream_id,
                # some mypy lint error patching here
                cast(dict[bytes | memoryview | str | int | float, bytes | memoryview | str | int | float], values),
                id=f'{timestamp}-*',
            )
        except RedisError as e:
            logging.error(f'Error while saving stream data, stream ID: {stream_id}, details: {str(e)}')
            raise IStreamDbError from None

    async def delete(self, stream_id: str, ids: Iterable[str]) -> int:
        try:
            return await self.__db.xdel(stream_id, *[ts_id for ts_id in ids])
        except RedisError as e:
            logging.error(f'Error while deleting from stream, stream ID: {stream_id}, details: {str(e)}')
            raise IStreamDbError from None

    async def read(self, stream_id: str, timestamp_id: str) -> dict[str, bytes]:
        try:
            values = await self.__db.xrange(stream_id, timestamp_id, timestamp_id, count=1)
            # transform to dict[str, str] here
            return {str(key): value for key, value in values[1].items()} if values else dict()
        except RedisError as e:
            logging.error(f'Error while deleting from stream, stream ID: {stream_id}, details: {str(e)}')
            raise IStreamDbError from None

    async def fetch_records(
        self, stream_id: str, start_ts: int, end_ts: Optional[int] = None
    ) -> AsyncGenerator[tuple[str, dict[str, bytes]], None]:
        # here we will try to make some bundle read from redis for better performance
        try:
            start_ts_id = str(start_ts)
            end_ts_id = f'{end_ts}-*' if end_ts is not None else '+'
            while True:
                values = await self.__db.xrange(stream_id, start_ts_id, end_ts_id, count=self.__max_bundle_size)
                if len(values):
                    for value in values:
                        # transform to dict[str, str] here
                        yield str(value[0]), ({str(k): v for k, v in value[1].items()} if value else dict())
                    # calculate first record ID for next fecth
                    last_fetched_id = values[-1][0]  # split into parts, suppose ID has {numbers}-{numbers} structure
                    last_fetched_id_parts = last_fetched_id.split['-']
                    start_ts_id = f'{last_fetched_id_parts[0]}-{int(last_fetched_id_parts[1])+1}'
                else:
                    # nothing fetched
                    return
        except RedisError as e:
            logging.error(f'Error while reading from stream, stream ID: {stream_id}, details: {str(e)}')
            raise IStreamDbError from None
