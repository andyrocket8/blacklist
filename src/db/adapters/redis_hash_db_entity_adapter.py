# redis hash DB Entity adapter (store str values only)
from typing import Any
from typing import AsyncGenerator
from typing import Awaitable
from typing import Iterable
from typing import Optional
from typing import cast

from redis.asyncio import Redis as RedisAsyncio

from src.db.base_hash_db_entity import IHashDbEntity


class RedisDBEntityAdapter(IHashDbEntity[str, str, str]):
    def __init__(self, db: RedisAsyncio):
        self.__db: RedisAsyncio = db

    async def write_values(self, hash_id: str, items: Iterable[tuple[str, str]]) -> int:
        """Write data to hash storage"""
        return await cast(Awaitable[int], self.__db.hset(hash_id, mapping={key: value for key, value in items}))

    async def delete_values(self, hash_id: str, items_keys: Iterable[str]) -> int:
        """Delete data from hash storage"""
        return await cast(Awaitable[int], self.__db.hdel(hash_id, *[cast(Any, key) for key in items_keys]))

    async def read_value(self, hash_id: str, key: str) -> Optional[str]:
        """Read data from hash storage"""
        return await cast(Awaitable[Optional[str]], self.__db.hget(hash_id, key))

    async def fetch_records(self, hash_id: str) -> AsyncGenerator[tuple[str, str], None]:
        """Read data from hash storage"""
        async for record in self.__db.hscan_iter(hash_id):
            yield cast(tuple[str, str], (record[0], record[1]))

    async def count(self, hash_id: str) -> int:
        """Returns count for specified hash_id"""
        return await cast(Awaitable[int], self.__db.hlen(hash_id))

    async def contains(self, hash_id: str, key: str) -> bool:
        """Returns whether key exists in hash_id"""
        return await cast(Awaitable[bool], self.__db.hexists(hash_id, key))
