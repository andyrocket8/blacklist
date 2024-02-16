# TODO Compose: tests for DB adapters (based on MemoryStorage)
from dataclasses import dataclass
from datetime import date as dt_date

import pytest

# from .test_memory_set_storage import MemorySetStorage


@dataclass(frozen=True)
class Car:
    brand: str
    color: str
    date_of_production: dt_date


@pytest.mark.asyncio
async def test_memory_set_db():
    # storage_obj = MemorySetStorage[str, Car]()
    # memory_set_db = storage_obj.set_db_adapter()
    pass
