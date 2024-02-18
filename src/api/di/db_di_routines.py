# Dependency Injection utilities
from typing import AsyncGenerator

from src.db.adapters.hash_db_entity_str_adapter import HashDbEntityGroupDataStrAdapter
from src.db.adapters.redis_hash_db_entity_adapter import RedisDBEntityAdapter
from src.db.base_hash_db_entity import IHashDbEntity
from src.db.storages.redis_db import redis_client


async def groups_db_service_adapter() -> AsyncGenerator[IHashDbEntity, None]:
    """DI for working with HashDbEntityGroupData.
    In further can depend on any storage for testing purposes"""
    async for client_obj in redis_client():
        yield HashDbEntityGroupDataStrAdapter(RedisDBEntityAdapter(client_obj))
