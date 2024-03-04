# Dependency Injection utilities
import logging
from typing import AsyncGenerator
from typing import Optional
from uuid import UUID

from src.db.adapters.hash_db_entity_str_adapter import HashDbEntityGroupDataStrAdapter
from src.db.adapters.redis_hash_db_entity_adapter import RedisDBEntityAdapter
from src.db.adapters.redis_set_db_adapter import RedisSetDbAdapter
from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.redis_stream_db_adapter import RedisStreamDbAdapter
from src.db.adapters.redis_union_set_db_adapter import RedisUnionSetDbAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpNetwork
from src.db.adapters.set_db_str_adapter import SetDbStrAdapterUUID
from src.db.adapters.union_set_db_str_adapter import UnionSetDbTransformUUIDAdapter
from src.db.adapters.union_set_db_str_adapter import generate_str_uuid
from src.db.adapters.usage_stream_db_adapter import UsageStreamRedisAdapter
from src.db.base_hash_db_entity import IHashDbEntity
from src.db.base_set_db import ISetDb
from src.db.base_set_db_entity import ISetDbEntity
from src.db.base_stream_db import IStreamDb
from src.db.storages.redis_db import context_async_redis_client
from src.db.storages.redis_db import redis_client
from src.schemas.usage_schemas import StreamUsageRecord
from src.service.history_db_service import HistoryDBService
from src.service.service_db_factories import ServiceAdapters
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


async def download_handle_adapters() -> AsyncGenerator[ServiceAdapters, None]:
    async with context_async_redis_client('download handler') as client_obj:
        # use one redis connection
        logging.debug('Provide download handle adapter')
        yield ServiceAdapters(
            address_set_db_entity=SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(client_obj)),
            network_set_db_entity=SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(client_obj)),
            hash_db_service=HashDbEntityGroupDataStrAdapter(RedisDBEntityAdapter(client_obj)),
            set_db=SetDbStrAdapterUUID(RedisSetDbAdapter(client_obj)),
            union_set_db=UnionSetDbTransformUUIDAdapter(RedisUnionSetDbAdapter(client_obj, generate_str_uuid)),
        )
        logging.debug('Finished providing download handle adapter')


async def get_set_db_adapter() -> AsyncGenerator[ISetDb, None]:
    async with context_async_redis_client('set management job') as client_obj:
        logging.debug('Provide set db adapter')
        yield SetDbStrAdapterUUID(RedisSetDbAdapter(client_obj))
        logging.debug('Finished providing set db adapter')


# Stream DB DI routines
async def get_stream_db_adapter() -> AsyncGenerator[IStreamDb[UUID, str, StreamUsageRecord], None]:
    """Getting stream DB object for Redis interaction (as generator call)"""
    async for client_obj in redis_client():
        yield UsageStreamRedisAdapter(RedisStreamDbAdapter(client_obj))


async def get_stream_db_adapter_job(
    job_name: Optional[str] = None,
) -> AsyncGenerator[IStreamDb[UUID, str, StreamUsageRecord], None]:
    """Getting stream DB object for Redis interaction (with context manager)"""
    async with context_async_redis_client(job_name if job_name is not None else 'stream management job') as client_obj:
        logging.debug('Provide stream db adapter')
        yield UsageStreamRedisAdapter(RedisStreamDbAdapter(client_obj))
        logging.debug('Finished providing stream db adapter')


# HKEY redis DI routines
async def get_history_db_service() -> AsyncGenerator[HistoryDBService, None]:
    async for client_obj in redis_client():
        yield HistoryDBService(client_obj)


async def get_history_db_service_for_job(job_name: Optional[str] = None) -> AsyncGenerator[HistoryDBService, None]:
    async with context_async_redis_client(
        job_name if job_name is not None else 'history db management job'
    ) as client_obj:
        logging.debug('Provide history db service object')
        yield HistoryDBService(client_obj)
        logging.debug('Finished providing history db service object')
