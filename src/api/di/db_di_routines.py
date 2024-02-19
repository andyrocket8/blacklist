# Dependency Injection utilities
from typing import AsyncGenerator

from src.db.adapters.hash_db_entity_str_adapter import HashDbEntityGroupDataStrAdapter
from src.db.adapters.redis_hash_db_entity_adapter import RedisDBEntityAdapter
from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.base_hash_db_entity import IHashDbEntity
from src.db.base_set_db_entity import ISetDbEntity
from src.db.storages.redis_db import redis_client
from src.service.service_db_factories import ServiceWithGroupDbAdapters


async def groups_db_service_adapter() -> AsyncGenerator[IHashDbEntity, None]:
    """DI for working with HashDbEntityGroupData.
    In further can depend on any storage for testing purposes"""
    async for client_obj in redis_client():
        yield HashDbEntityGroupDataStrAdapter(RedisDBEntityAdapter(client_obj))


async def address_db_service_adapter() -> AsyncGenerator[ISetDbEntity, None]:
    """DI for working with SetDbEntity
    In further can depend on any storage for testing purposes
    """
    async for client_obj in redis_client():
        yield SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(client_obj))


async def address_with_groups_db_service_adapter() -> AsyncGenerator[ServiceWithGroupDbAdapters, None]:
    async for client_obj in redis_client():
        yield ServiceWithGroupDbAdapters(
            db_service_adapter=SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(client_obj)),
            db_hash_service_adapter=HashDbEntityGroupDataStrAdapter(RedisDBEntityAdapter(client_obj)),
        )
