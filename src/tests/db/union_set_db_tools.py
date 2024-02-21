import pytest

from src.db.base_set_db import ISetDb
from src.db.base_set_db_entity import ISetDbEntity
from src.db.base_union_set_db import IUnionSetDb
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .test_set_db_classes import SetTestData


@pytest.mark.asyncio
async def run_test_union_set_db_entity(
    set_db_entity_test_data: list[SetTestData[K, V]],
    set_db_obj: ISetDb[K],
    union_set_db_obj: IUnionSetDb[K],
    set_db_entity_obj: ISetDbEntity[K, V],
):
    check_set_data: dict[K, set[V]] = dict()
    # checking addition to set
    for test_record in set_db_entity_test_data:
        added_records: int = await set_db_entity_obj.add_to_set(test_record.set_id, test_record.set_data)
        check_set_data[test_record.set_id] = set(test_record.set_data)
        assert len(check_set_data[test_record.set_id]) == added_records, 'Wrong length of loaded set in storage'
        for value in check_set_data[test_record.set_id]:
            assert await set_db_entity_obj.contains(
                test_record.set_id, value
            ), 'Expect existence of record of in-memory standard set with stored in the storage'
    # checking sets intersection
    merged_sets_ids: list[K] = list()
    for i in range(len(set_db_entity_test_data) - 1):
        first_set_id = set_db_entity_test_data[i].set_id
        second_set_id = set_db_entity_test_data[i + 1].set_id
        united_set_id: K = await union_set_db_obj.union_set((first_set_id, second_set_id))
        united_set: set[V] = check_set_data[first_set_id] | check_set_data[second_set_id]
        assert len(united_set) == await set_db_entity_obj.count(
            united_set_id
        ), 'Length of standard in-memory united set must be the same as united in the storage'
        # check content
        for value in united_set:
            assert await set_db_entity_obj.contains(
                united_set_id, value
            ), 'Expect existence of record of in-memory standard united set with stored in the storage'
        # store merged set id in list for further teardown
        merged_sets_ids.append(united_set_id)
    # union all sets
    united_set_id = await union_set_db_obj.union_set(x.set_id for x in set_db_entity_test_data)
    result_set: set[V] = set()
    for record in set_db_entity_test_data:
        result_set |= set(record.set_data)
    assert len(result_set) == await set_db_entity_obj.count(
        united_set_id
    ), 'United length of set should be the same as in storage (all test sets)'
    for value in result_set:
        assert await set_db_entity_obj.contains(
            united_set_id, value
        ), 'Expect existence of record of in-memory standard united set with stored in the storage'
    merged_sets_ids.append(united_set_id)
    # teardown test execution
    for set_id in merged_sets_ids:
        await set_db_obj.del_set(set_id)
