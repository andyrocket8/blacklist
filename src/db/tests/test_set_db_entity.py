from uuid import UUID

import pytest

from src.db.memory_set_storage import MemorySetStorage

from .set_db_entity_base_tools import run_test_set_db_entity
from .test_memory_set_storage import STORAGE_DATA_ATTR
from .test_set_db_classes import Car
from .test_set_db_classes import SetDbEntityStrCarAdapter


@pytest.mark.asyncio
async def test_typed_memory_set_db(car_set_test_data, car_set_absent_test_data):
    # TODO refactor to pytest fixtures
    storage_obj = MemorySetStorage[UUID, Car]()
    set_db_entity_obj = storage_obj.set_db_entity_adapter()
    await run_test_set_db_entity(car_set_test_data, car_set_absent_test_data, set_db_entity_obj)


@pytest.mark.asyncio
async def test_adopted_memory_set_db(car_set_test_data, car_set_absent_test_data):
    # TODO refactor to pytest fixtures
    storage_obj = MemorySetStorage[str, str]()
    set_db_entity_obj = SetDbEntityStrCarAdapter(storage_obj.set_db_entity_adapter())
    await run_test_set_db_entity(car_set_test_data, car_set_absent_test_data, set_db_entity_obj)
    print(storage_obj.__dict__[STORAGE_DATA_ATTR])
