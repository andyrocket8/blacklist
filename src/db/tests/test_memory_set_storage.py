# TODO Compose: tests for MemorySetStorage
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from uuid import uuid4

import pytest

from src.db.memory_set_storage import MemorySetStorage

STORAGE_DATA_ATTR = '_MemorySetStorage__data'


@dataclass(frozen=True)
class PersonData:
    last_name: str
    first_name: str
    middle_name: Optional[str]
    age: int


@dataclass
class SetRecord:
    set_id: UUID
    values: tuple[PersonData, ...]


@pytest.fixture()
def person_data_set_1() -> SetRecord:
    return SetRecord(
        uuid4(),
        (
            PersonData('Ivanov', 'Ivan', None, 35),
            PersonData('Drozdova', 'Veronika', 'Petrovna', 30),
        ),
    )


@pytest.fixture()
def person_data_set_2() -> SetRecord:
    return SetRecord(
        uuid4(),
        (
            PersonData('Beloglazov', 'Victor', 'Petrovich', 41),
            PersonData('Ganshin', 'Ivan', 'Nikolaevich', 50),
            PersonData('Drozdova', 'Veronika', 'Petrovna', 30),
        ),
    )


@pytest.mark.asyncio
async def test_memory_set_storage(person_data_set_1, person_data_set_2):
    # initiate the storage
    simple_ms_obj = MemorySetStorage[UUID, PersonData]()

    # add data to storage
    set_1_id = person_data_set_1.set_id
    await simple_ms_obj.write_to_set(set_1_id, person_data_set_1.values)
    set_2_id = person_data_set_2.set_id
    await simple_ms_obj.write_to_set(set_2_id, person_data_set_2.values)
    # checking storage existence with exists operation (existent set)
    assert simple_ms_obj.exists(set_1_id) == 1, 'exists should return 1 for existent set (1)'
    assert simple_ms_obj.exists(set_2_id) == 1, 'exists should return 1 for existent set (2)'
    # checking storage existence with exists operation (absent set)
    assert simple_ms_obj.exists(uuid4()) == 0, 'exists should return 0 for nonexistent set'
    # testing get_set and contains
    set_1 = simple_ms_obj.get_set(set_1_id)
    for person_data in person_data_set_1.values:
        assert person_data in set_1, f'Assume {person_data} is in python set (internal storage)'
        assert simple_ms_obj.contains(
            set_1_id, person_data
        ), f'Assume {person_data} is in memory set (internal storage)'
    # test count for set
    assert simple_ms_obj.count(set_1_id) == len(person_data_set_1.values), 'Error on checking length of set 1'
    assert simple_ms_obj.count(set_2_id) == len(person_data_set_2.values), 'Error on checking length of set 2'
    # test copy set
    set_copy_id = uuid4()
    result = simple_ms_obj.copy_set(set_2_id, set_copy_id)
    assert result == 1, 'Assume 1 on productive set copy'
    # checking length
    assert simple_ms_obj.count(set_copy_id) == len(
        person_data_set_2.values
    ), 'Error on checking length of copy of set 2'
    # checking contents
    counter = 0
    async for person_data in simple_ms_obj.fetch_records(set_copy_id):
        assert person_data in person_data_set_2.values, f'Not found data from set 2 in copy of set 2, step: {counter}'
        counter += 1
    # checking counter
    assert counter == len(person_data_set_2.values), 'Mismatch of records length in set copy 2'
    # checking deletion operation on set 2
    result = await simple_ms_obj.del_from_set(set_2_id, person_data_set_2.values[: len(person_data_set_2.values) - 1])
    assert result == len(person_data_set_2.values) - 1, 'Assume we got 1 on successful deletion operation'
    # checking length of set (should be 1)
    assert simple_ms_obj.count(set_2_id) == 1, 'Error on checking length of set 2'
    # checking existence of last record
    assert simple_ms_obj.contains(set_2_id, person_data_set_2.values[-1]), 'Assume existence of last record in set 2'
    # test copy t oexistent set
    result = simple_ms_obj.copy_set(set_2_id, set_copy_id)
    assert result == 0, 'Assume 0 on empty set copy'
    # checking length
    assert simple_ms_obj.count(set_copy_id) == len(
        person_data_set_2.values
    ), 'Error on checking length of copy of set 2 after failed copy'
    # test remove operation
    assert simple_ms_obj.remove_set(set_2_id) == 1, 'Should be 1 on productive set deletion'
    assert simple_ms_obj.count(set_2_id) == 0, 'Should be 0 on absent set'
    assert not simple_ms_obj.exists(set_2_id), 'Should be False on absent set'
    assert simple_ms_obj.remove_set(set_2_id) == 0, 'Should be 1 on empty set deletion'
    assert len(simple_ms_obj.__dict__[STORAGE_DATA_ATTR]) == 2, 'Should contain only 2 sets'
    # testing copy with replace
    result = simple_ms_obj.copy_set(set_1_id, set_copy_id, with_replace=True)
    assert result == 1, 'Assume 1 on productive set copy with replace'
    # Checking contents of set
    counter = 0
    async for person_data in simple_ms_obj.fetch_records(set_copy_id):
        assert person_data in person_data_set_1.values, f'Not found data from set 1 in copy of set, step: {counter}'
        counter += 1
    # checking counter
    assert counter == len(person_data_set_1.values), 'Mismatch of records length in set copy from set 1'
    assert simple_ms_obj.count(set_copy_id) == len(person_data_set_1.values), 'Error on checking length of copied set'
    # checking sets count
    assert (
        len(simple_ms_obj.__dict__[STORAGE_DATA_ATTR]) == 2
    ), 'Should contain again 2 sets now (was copy with replace)'
    # print(simple_ms_obj.__dict__[STORAGE_DATA_ATTR])


if __name__ == '__main__':
    pytest.main()
