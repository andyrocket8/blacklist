# Some tests for UnionSetDb classes
from dataclasses import dataclass
from typing import AsyncGenerator
from typing import Generator
from uuid import UUID
from uuid import uuid4

import pytest
import pytest_asyncio
from redis.asyncio import Redis as RedisAsyncio

from src.db.adapters.redis_set_db_adapter import RedisSetDbAdapter
from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.redis_union_set_db_adapter import RedisUnionSetDbAdapter
from src.db.adapters.set_db_str_adapter import SetDbStrAdapterUUID
from src.db.adapters.union_set_db_str_adapter import UnionSetDbTransformUUIDAdapter
from src.db.adapters.union_set_db_str_adapter import generate_str_uuid
from src.db.base_set_db import ISetDb
from src.db.base_set_db_entity import ISetDbEntity
from src.db.base_union_set_db import IUnionSetDb
from src.db.storages.memory_set_storage import MemorySetStorage

from .test_set_db_classes import SetDbEntityStrIntAdapter
from .test_set_db_classes import SetTestData
from .union_set_db_tools import run_test_union_set_db_entity


@pytest.fixture(scope='function')
def memory_typed_storage_obj() -> Generator[MemorySetStorage[UUID, int], None, None]:
    storage_obj = MemorySetStorage[UUID, int]()
    yield storage_obj


@pytest_asyncio.fixture
async def memory_set_typed_db(
    memory_typed_storage_obj, union_set_test_data: list[SetTestData[UUID, int]]
) -> AsyncGenerator[ISetDb, None]:
    db_entity_obj = memory_typed_storage_obj.set_db_adapter()
    yield db_entity_obj
    # teardown test execution
    for test_record in union_set_test_data:
        await db_entity_obj.del_set(test_record.set_id)


@pytest.fixture
def memory_union_set_typed_db(memory_typed_storage_obj) -> Generator[IUnionSetDb, None, None]:
    db_union_set_obj = memory_typed_storage_obj.union_set_db_adapter(uuid4)
    yield db_union_set_obj


@pytest.fixture
def memory_set_typed_db_entity(memory_typed_storage_obj) -> Generator[ISetDbEntity, None, None]:
    """Fixture with typed memory set db entity"""
    set_db_entity_obj = memory_typed_storage_obj.set_db_entity_adapter()
    yield set_db_entity_obj


@pytest.mark.asyncio
async def test_memory_union_set_typed_db(
    union_set_test_data: list[SetTestData[UUID, int]],
    memory_set_typed_db: ISetDb,
    memory_union_set_typed_db: IUnionSetDb,
    memory_set_typed_db_entity: ISetDbEntity,
):
    await run_test_union_set_db_entity(
        union_set_test_data, memory_set_typed_db, memory_union_set_typed_db, memory_set_typed_db_entity
    )


# Test with Redis storage
@dataclass
class RedisSetDbFixtureData:
    redis_set_str_db: ISetDb
    redis_union_set_str_db: IUnionSetDb
    redis_set_str_db_entity: ISetDbEntity
    union_set_test_data: list[SetTestData[UUID, int]]


@pytest_asyncio.fixture
async def redis_set_fixture_test_data(
    redis_connection_pool, union_set_test_data: list[SetTestData[UUID, int]]
) -> AsyncGenerator[RedisSetDbFixtureData, None]:
    """Fixture with str memory set db entity"""
    client = RedisAsyncio.from_pool(redis_connection_pool.connection_pool)
    set_db_entity_obj = SetDbEntityStrIntAdapter(RedisSetDbEntityAdapter(client))
    set_db_obj = SetDbStrAdapterUUID(RedisSetDbAdapter(client))
    set_union_db_obj = UnionSetDbTransformUUIDAdapter(RedisUnionSetDbAdapter(client, generate_str_uuid))
    yield RedisSetDbFixtureData(set_db_obj, set_union_db_obj, set_db_entity_obj, union_set_test_data)
    # teardown created data
    for record in union_set_test_data:
        await set_db_obj.del_set(record.set_id)


@pytest.mark.asyncio
async def test_redis_set_db_entity(
    redis_set_fixture_test_data: RedisSetDbFixtureData,
):
    print('Executing redis test')
    await run_test_union_set_db_entity(
        redis_set_fixture_test_data.union_set_test_data,
        redis_set_fixture_test_data.redis_set_str_db,
        redis_set_fixture_test_data.redis_union_set_str_db,
        redis_set_fixture_test_data.redis_set_str_db_entity,
    )
