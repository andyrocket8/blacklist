# TODO Compose: tests for DB adapters (based on MemoryStorage and Redis)
import dataclasses
from typing import AsyncGenerator
from typing import Generator
from uuid import UUID
from uuid import uuid4

import pytest
import pytest_asyncio
from redis.asyncio import Redis as RedisAsyncio

from src.db.adapters.redis_set_db_adapter import RedisSetDbAdapter
from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_str_adapter import SetDbStrAdapterUUID
from src.db.base_set_db import ISetDb
from src.db.base_set_db_entity import ISetDbEntity
from src.db.storages.memory_set_storage import MemorySetStorage

from .classes_for_set_db_test import Car
from .classes_for_set_db_test import SetDbEntityStrCarAdapter
from .classes_for_set_db_test import SetTestData
from .test_memory_set_storage import STORAGE_DATA_ATTR
from .tools_for_set_db_test import run_test_set_db
from .tools_for_set_db_test import teardown_test_set_db


@pytest.fixture(scope='function')
def memory_typed_storage_obj() -> Generator[MemorySetStorage[UUID, Car], None, None]:
    storage_obj = MemorySetStorage[UUID, Car]()
    yield storage_obj
    print('memory_set_typed_db_entity: ', storage_obj.__dict__[STORAGE_DATA_ATTR])


@pytest.fixture
def memory_set_typed_db_entity(memory_typed_storage_obj) -> Generator[ISetDbEntity, None, None]:
    """Fixture with typed memory set db entity"""
    set_db_entity_obj = memory_typed_storage_obj.set_db_entity_adapter()
    yield set_db_entity_obj


@pytest.fixture
def memory_set_typed_db(memory_typed_storage_obj) -> Generator[ISetDb, None, None]:
    db_entity_obj = memory_typed_storage_obj.set_db_adapter()
    yield db_entity_obj


@pytest.mark.asyncio
async def test_memory_set_typed_db(
    car_set_test_data: list[SetTestData[UUID, Car]],
    memory_set_typed_db_entity: ISetDbEntity,
    memory_set_typed_db: ISetDb,
):
    await run_test_set_db(car_set_test_data, memory_set_typed_db_entity, memory_set_typed_db, uuid4)


@pytest.fixture(scope='function')
def memory_str_storage_obj() -> Generator[MemorySetStorage[str, str], None, None]:
    storage_obj = MemorySetStorage[str, str]()
    yield storage_obj
    print('memory_str_storage_obj: ', storage_obj.__dict__[STORAGE_DATA_ATTR])


@pytest.fixture
def memory_set_str_db_entity(memory_str_storage_obj) -> Generator[ISetDbEntity, None, None]:
    """Fixture with typed memory set db entity"""
    set_db_entity_obj: ISetDbEntity = SetDbEntityStrCarAdapter(memory_str_storage_obj.set_db_entity_adapter())
    yield set_db_entity_obj


@pytest.fixture
def memory_set_str_db(memory_str_storage_obj) -> Generator[ISetDb, None, None]:
    db_entity_obj: ISetDb = SetDbStrAdapterUUID(memory_str_storage_obj.set_db_adapter())
    yield db_entity_obj


@pytest.mark.asyncio
async def test_memory_set_str_db(
    car_set_test_data: list[SetTestData[UUID, Car]],
    memory_set_str_db_entity: ISetDbEntity[UUID, Car],
    memory_set_str_db: ISetDb[UUID],
):
    await run_test_set_db(car_set_test_data, memory_set_str_db_entity, memory_set_str_db, uuid4)


@dataclasses.dataclass
class RedisSetDbFixtureData:
    redis_set_str_db_entity: ISetDbEntity
    redis_set_str_db: ISetDb
    car_set_test_data: list[SetTestData]


@pytest_asyncio.fixture
async def redis_set_str_db_data(
    redis_connection_pool, car_set_test_data: list[SetTestData]
) -> AsyncGenerator[RedisSetDbFixtureData, None]:
    """Fixture with str memory set db entity"""
    client = RedisAsyncio.from_pool(redis_connection_pool.connection_pool)
    set_db_entity_obj = SetDbEntityStrCarAdapter(RedisSetDbEntityAdapter(client))
    set_db_obj = SetDbStrAdapterUUID(RedisSetDbAdapter(client))
    yield RedisSetDbFixtureData(set_db_entity_obj, set_db_obj, car_set_test_data)
    # teardown created data
    await teardown_test_set_db(
        car_set_test_data,
        set_db_obj,
    )


@pytest.mark.asyncio
async def test_redis_set_db_entity(
    redis_set_str_db_data: RedisSetDbFixtureData,
):
    print('Executing redis test')
    await run_test_set_db(
        redis_set_str_db_data.car_set_test_data,
        redis_set_str_db_data.redis_set_str_db_entity,
        redis_set_str_db_data.redis_set_str_db,
        uuid4,
    )
