import dataclasses
from typing import AsyncGenerator
from typing import Generator

import pytest
import pytest_asyncio
from redis.asyncio import Redis as RedisAsyncio

from src.db.adapters.memory_hash_db_entity_adapter import MemoryHashDbEntity
from src.db.adapters.redis_hash_db_entity_adapter import RedisDBEntityAdapter
from src.db.base_hash_db_entity import IHashDbEntity
from src.db.storages.memory_hash_storage import STORAGE_DATA_ATTR
from src.db.storages.memory_hash_storage import MemoryHashStorage
from src.tests.db.classes_for_hash_db_test import HashDbEntityNetworkInfoAdapter

from .classes_for_hash_db_test import NetworkInfo
from .tools_for_hash_db_entity_test import run_test_hash_db_entity


@pytest.fixture
def memory_hash_typed_db_entity() -> Generator[IHashDbEntity, None, None]:
    storage_obj: MemoryHashStorage = MemoryHashStorage()
    yield MemoryHashDbEntity(storage_obj)
    print(storage_obj.__dict__[STORAGE_DATA_ATTR])


@pytest.fixture
def memory_hash_str_db_entity() -> Generator[IHashDbEntity, None, None]:
    storage_obj: MemoryHashStorage[str, str, str] = MemoryHashStorage()
    yield HashDbEntityNetworkInfoAdapter(MemoryHashDbEntity(storage_obj))
    print(storage_obj.__dict__[STORAGE_DATA_ATTR])


@pytest.mark.asyncio
async def test_memory_hash_typed_db_entity(
    memory_hash_typed_db_entity: IHashDbEntity, company_network_info_for_test: list[NetworkInfo]
):
    assert len(company_network_info_for_test) == 3, 'Expect len of test data == 3'
    await run_test_hash_db_entity(memory_hash_typed_db_entity, company_network_info_for_test)


@pytest.mark.asyncio
async def test_memory_hash_str_db_entity(
    memory_hash_str_db_entity: IHashDbEntity, company_network_info_for_test: list[NetworkInfo]
):
    assert len(company_network_info_for_test) == 3, 'Expect len of test data == 3'
    await run_test_hash_db_entity(memory_hash_str_db_entity, company_network_info_for_test)


@dataclasses.dataclass
class RedisHashDbEntityFixtureData:
    redis_hash_db_entity: IHashDbEntity
    test_data: list[NetworkInfo]


@pytest_asyncio.fixture
async def redis_hash_db_entity_data(
    redis_connection_pool, company_network_info_for_test: list[NetworkInfo]
) -> AsyncGenerator[RedisHashDbEntityFixtureData, None]:
    """Fixture with str memory set db entity"""
    client = RedisAsyncio.from_pool(redis_connection_pool.connection_pool)
    set_db_entity_obj = HashDbEntityNetworkInfoAdapter(RedisDBEntityAdapter(client))
    yield RedisHashDbEntityFixtureData(set_db_entity_obj, company_network_info_for_test)
    # teardown created data
    pass


@pytest.mark.asyncio
async def test_redis_hash_db_entity(
    redis_hash_db_entity_data: RedisHashDbEntityFixtureData,
):
    print('Executing redis test')
    await run_test_hash_db_entity(redis_hash_db_entity_data.redis_hash_db_entity, redis_hash_db_entity_data.test_data)
