from dataclasses import dataclass
from datetime import date as dt_date
from uuid import UUID
from uuid import uuid4

import pytest

from src.db.memory_set_storage import MemorySetStorage

from .set_db_entity_base_tools import SetTestData
from .set_db_entity_base_tools import run_test_set_db_entity


@dataclass(frozen=True)
class Car:
    brand: str
    model: str
    color: str
    date_of_registration: dt_date
    registration_no: str


TEST_CAR_SETS_DATA: list[SetTestData[UUID, Car]] = [
    SetTestData(
        uuid4(),
        (
            Car('Mercedes', 'GLK', 'Red', dt_date(2010, 1, 12), 'A100AA50'),
            Car('BMW', 'X5', 'Blue', dt_date(2019, 11, 29), 'X187XX150'),
            Car('Ford', 'Mustang', 'Grey', dt_date(2018, 5, 23), 'P123HY199'),
            Car('Mercedes', 'VITO', 'Black', dt_date(2021, 7, 30), 'M966HH77'),
            Car('Toyota', 'Camry', 'Yellow', dt_date(2022, 12, 24), 'O544PO177'),
        ),
    ),
    SetTestData(
        uuid4(),
        (
            Car('Audi', 'A6', 'White', dt_date(2016, 2, 28), 'K776TP199'),
            Car('Hyundai', 'Accent', 'Grey', dt_date(2008, 2, 1), 'Y223XH77'),
            Car('Renault', 'Laguna', 'Light Grey', dt_date(2018, 5, 23), 'A231AA77'),
        ),
    ),
    SetTestData(
        uuid4(),
        (
            Car('Ferrari', 'California', 'Red', dt_date(2013, 10, 17), 'A001AA99'),
            Car('Peugeot', '206', 'Pink', dt_date(2008, 3, 24), 'P206PP177'),
            Car('Lamborghini', 'Diablo', 'Panther Black', dt_date(2020, 10, 23), 'X002XX77'),
        ),
    ),
]

TEST_CAR_SETS_ABSENT_DATA: list[Car] = [
    Car('Honda', 'Pilot', 'Dark grey', dt_date(2013, 8, 15), 'X003XX99'),
    Car('Renault', 'Duster', 'White', dt_date(2021, 2, 1), 'B785AX77'),
    Car('Toyota', 'RAV4', 'Blue', dt_date(2021, 7, 7), 'K223KK190'),
    Car('Toyota', 'Prius', 'Grey (as most of them)', dt_date(2018, 1, 31), 'P300KK23'),
    Car('VAZ', '21099', 'Rusty', dt_date(1996, 12, 31), 'M100MX77'),
]


@pytest.mark.asyncio
async def test_memory_set_db():
    storage_obj = MemorySetStorage[UUID, Car]()
    set_db_entity_obj = storage_obj.set_db_entity_adapter()
    await run_test_set_db_entity(TEST_CAR_SETS_DATA, TEST_CAR_SETS_ABSENT_DATA, set_db_entity_obj)
