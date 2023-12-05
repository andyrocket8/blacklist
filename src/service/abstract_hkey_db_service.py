import json
from typing import Any
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
        return await cast(Awaitable[Any], self.db.hdel(str(self.set_id), [record_id]))
