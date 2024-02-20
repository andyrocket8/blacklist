from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Iterable
from typing import cast

from redis.asyncio import Redis as RedisAsyncio

from src.db.base_union_set_db import IUnionSetDb


class RedisUnionSetDbAdapter(IUnionSetDb[str]):
    def __init__(self, db: RedisAsyncio, key_generator: Callable[[], str]):
        self.__db: RedisAsyncio = db
        self.__key_generator = key_generator

    async def union_set(self, set_identities: Iterable[str]) -> str:
        """Union sets and return new set identity"""
        new_set_id: str = self.__key_generator()
        await cast(Awaitable[Any], self.__db.sunionstore(new_set_id, [set_id for set_id in set_identities]))
        return new_set_id
