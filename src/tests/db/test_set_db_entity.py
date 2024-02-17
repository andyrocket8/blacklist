import dataclasses
from typing import AsyncGenerator
from typing import Generator
from uuid import UUID

import pytest
import pytest_asyncio
from redis.asyncio import Redis as RedisAsyncio

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.base_set_db_entity import ISetDbEntity
from src.db.storages.memory_set_storage import MemorySetStorage

from .set_db_entity_base_tools import run_test_set_db_entity
from .set_db_entity_base_tools import teardown_test_set_db_entity
from .test_memory_set_storage import STORAGE_DATA_ATTR
from .test_set_db_classes import Car
from .test_set_db_classes import SetDbEntityStrCarAdapter
from .test_set_db_classes import SetTestData


@pytest.fixture
def memory_set_typed_db_entity() -> Generator[ISetDbEntity, None, None]:
    """Fixture with typed memory set db entity"""
    storage_obj = MemorySetStorage[UUID, Car]()
    set_db_entity_obj = storage_obj.set_db_entity_adapter()
    yield set_db_entity_obj
    print('memory_set_typed_db_entity: ', storage_obj.__dict__[STORAGE_DATA_ATTR])


@pytest.fixture
def memory_set_str_db_entity() -> Generator[ISetDbEntity, None, None]:
    """Fixture with str memory set db entity"""
    storage_obj = MemorySetStorage[str, str]()
    set_db_entity_obj = SetDbEntityStrCarAdapter(storage_obj.set_db_entity_adapter())
    yield set_db_entity_obj
    print('memory_set_str_db_entity: ', storage_obj.__dict__[STORAGE_DATA_ATTR])


# Must execute separate test function because of separate initial fixtures.
# It's impossible to pass fixture forward as fixture param
@pytest.mark.asyncio
async def test_memory_set_typed_db_entity(
    memory_set_typed_db_entity: ISetDbEntity, car_set_test_data, car_set_absent_test_data
):
    await run_test_set_db_entity(car_set_test_data, car_set_absent_test_data, memory_set_typed_db_entity)


@pytest.mark.asyncio
async def test_memory_set_str_db_entity(
    memory_set_str_db_entity: ISetDbEntity, car_set_test_data, car_set_absent_test_data
):
    await run_test_set_db_entity(car_set_test_data, car_set_absent_test_data, memory_set_str_db_entity)


@dataclasses.dataclass
class RedisSetDbEntityFixtureData:
    redis_set_str_db_entity: ISetDbEntity
    car_set_test_data: list[SetTestData]
    car_set_absent_test_data: list[Car]


@pytest_asyncio.fixture
async def redis_set_str_db_entity_data(
    redis_connection_pool, car_set_test_data: list[SetTestData], car_set_absent_test_data: list[Car]
) -> AsyncGenerator[RedisSetDbEntityFixtureData, None]:
    """Fixture with str memory set db entity"""
    client = RedisAsyncio.from_pool(redis_connection_pool.connection_pool)
    set_db_entity_obj = SetDbEntityStrCarAdapter(RedisSetDbEntityAdapter(client))
    yield RedisSetDbEntityFixtureData(set_db_entity_obj, car_set_test_data, car_set_absent_test_data)
    # teardown created data
    await teardown_test_set_db_entity(
        car_set_test_data,
        car_set_absent_test_data,
        set_db_entity_obj,
    )


@pytest.mark.asyncio
async def test_redis_set_db_entity(
    redis_set_str_db_entity_data: RedisSetDbEntityFixtureData,
):
    print('Executing redis test')
    await run_test_set_db_entity(
        redis_set_str_db_entity_data.car_set_test_data,
        redis_set_str_db_entity_data.car_set_absent_test_data,
        redis_set_str_db_entity_data.redis_set_str_db_entity,
    )
