import json
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import cast
from uuid import UUID

from src.db.redis_db import RedisAsyncio

T = TypeVar('T')
TypeT = Type[T]

JE = TypeVar('JE', bound=json.JSONEncoder)
TypeJE = Type[JE]


class AbstractHkeyDBService(Generic[T, JE]):
    set_id: UUID
    service_type: TypeT
    json_encoder: TypeJE

    def __init__(self, db: RedisAsyncio, set_id: Optional[UUID] = None):
        self.db: RedisAsyncio = db
        self.set_id: UUID = set_id if set_id is not None else self.set_id

    async def write_record(self, record_id: str, data: T) -> int:
        return await cast(
            Awaitable[Any], self.db.hset(str(self.set_id), record_id, json.dumps(data, cls=self.json_encoder))
        )

    async def read_record(self, record_id: str) -> Optional[T]:
        data: Optional[str] = await cast(Awaitable[Any], self.db.hget(str(self.set_id), record_id))
        if data is not None:
            return self.service_type(**json.loads(data))
        return None

    async def delete_record(self, record_id: str) -> int:
        return await self.delete_records([record_id])

    async def delete_records(self, records: list[Any]) -> int:
        return await cast(Awaitable[Any], self.db.hdel(str(self.set_id), *records))

    async def get_records(
        self, limit: int = 0, offset: int = 0, match: str = '*'
    ) -> AsyncGenerator[tuple[T, str], None]:
        if limit or offset:
            # first get stored keys from hash (this can take a while)
            keys: list[str] = [s for s in await cast(Awaitable[list[Any]], self.db.hkeys(str(self.set_id)))]
            for key in keys[offset : offset + limit] if limit > 0 else keys[offset:]:
                read_record = await self.read_record(key)
                if read_record is not None:
                    yield read_record, key
        else:
            async for data in self.db.hscan_iter(str(self.set_id), match=match, count=1):
                json_data = json.loads(data[1])
                yield self.service_type(**json_data), data[0]
