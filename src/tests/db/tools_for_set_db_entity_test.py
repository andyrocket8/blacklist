# Methods for testing set db entities classes
from src.db.base_set_db_entity import ISetDbEntity
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .classes_for_set_db_test import SetTestData


async def check_sets_count(
    set_db_entity_obj: ISetDbEntity[K, V], set_test_data: SetTestData[K, V], expected_difference: int = 0
):
    """
    Iterate over test data and check storage set size against test sets
    :param set_db_entity_obj: testing set_db_entity
    :param set_test_data: list of SetTestData
    :param expected_difference: result correction (if some elements were added or removed)

    """
    assert (
        await set_db_entity_obj.count(set_test_data.set_id) == len(set_test_data.set_data) + expected_difference
    ), f'"check_sets_count" detect difference, checked data: {set_test_data}'


async def check_set_consistency(
    set_db_entity_obj: ISetDbEntity[K, V],
    set_test_data: SetTestData[K, V],
    set_test_absent_data: list[V],
):
    """Routine for checking set consistency"""
    # checking data in set
    async for record in set_db_entity_obj.fetch_records(set_test_data.set_id):
        assert record in set_test_data.set_data, f'Expect record {record} should be be in test set data'
        assert record not in set_test_absent_data, 'Expect absence of set data in storage data'
    # checking contains function
    for record in set_test_data.set_data:
        assert await set_db_entity_obj.contains(
            set_test_data.set_id, record
        ), f'Expect test set record {record} should be in storage data'
    for absent_record in set_test_absent_data:
        assert not await set_db_entity_obj.contains(
            set_test_data.set_id, absent_record
        ), f'Expect absense of record {absent_record} in storage data'


async def add_records_to_sets(
    set_db_entity_obj: ISetDbEntity[K, V], set_db_entity_test_data: list[SetTestData[K, V]]
) -> list[int]:
    result: list[int] = list()
    for test_record in set_db_entity_test_data:
        result.append(await set_db_entity_obj.add_to_set(test_record.set_id, test_record.set_data))
    return result


async def run_test_set_db_entity(
    set_db_entity_test_data: list[SetTestData[K, V]],
    set_db_entity_absent_data: list[V],
    set_db_entity_obj: ISetDbEntity[K, V],
):
    """
    Testing of set_db_entity. Should be called from pytest routines (abstract routine for any SetTestData)

    :param set_db_entity_test_data: set of data stored in storage. Should be greater than 2 records
    :param set_db_entity_absent_data: list of entities that should be absent in storage
    :param set_db_entity_obj: set_db_entity object
    :return: None

    Attention: on function change don't forget to change following 'teardown_set_db_entity' function
    """
    assert len(set_db_entity_test_data) > 2, 'Test data length should be greater than 2'
    assert len(set_db_entity_absent_data) > 2, 'Test data ob absent records should be greater than 2'
    # Add data of all test sets to ISetDbEntity
    records_added_list = await add_records_to_sets(set_db_entity_obj, set_db_entity_test_data)
    for step, step_add_result in enumerate(records_added_list):
        assert step_add_result == len(
            set_db_entity_test_data[step].set_data
        ), f'Expect to write all set data to set (Step {step})'
    for test_record in set_db_entity_test_data:
        # check sets consistency
        await check_set_consistency(set_db_entity_obj, test_record, set_db_entity_absent_data)
        # testing storage consistency
        await check_sets_count(set_db_entity_obj, test_record, 0)
    # Reading data from storage (test fetch operation)
    for step, test_record in enumerate(set_db_entity_test_data):
        async for record in set_db_entity_obj.fetch_records(test_record.set_id):
            assert (
                record in test_record.set_data
            ), f'Expect record {record} should be be in test set data, (Step {step})'
            assert record not in set_db_entity_absent_data, 'Expect absence of set data in storage data'
        # checking contains function
        for record in test_record.set_data:
            assert await set_db_entity_obj.contains(
                test_record.set_id, record
            ), f'Expect test set record {record} should be in storage data, (Step {step})'
        for absent_record in set_db_entity_absent_data:
            assert not await set_db_entity_obj.contains(
                test_record.set_id, absent_record
            ), f'Expect absense of record {absent_record} in storage data, (Step {step})'
    # Testing addition of extra and duplicated data (on set 1)
    # First of all add one record. We add dada from set_db_entity_absent_data, so on teardown operation we should
    # clear added records
    test_record = set_db_entity_test_data[0]
    new_record_1 = set_db_entity_absent_data[0]
    records_added = await set_db_entity_obj.add_to_set(test_record.set_id, [new_record_1])
    assert records_added == 1, 'Expect to write extra data (addition of absent data), iteration 1)'
    assert await set_db_entity_obj.contains(
        test_record.set_id, new_record_1
    ), f'Expect presence of record {new_record_1} in storage data, (addition of duplicated data), iteration 1'
    # modified data for iteration 1
    modified_data = SetTestData(test_record.set_id, test_record.set_data + (new_record_1,))
    modified_entity_absent_data = set_db_entity_absent_data[1:]
    # checking consistency of modified set
    await check_set_consistency(set_db_entity_obj, modified_data, modified_entity_absent_data)
    # checking count of records
    await check_sets_count(set_db_entity_obj, modified_data, 0)
    # Add two more record and check deduplication
    new_record_2 = set_db_entity_absent_data[1]
    new_record_3 = set_db_entity_absent_data[2]
    records_added = await set_db_entity_obj.add_to_set(test_record.set_id, [new_record_1, new_record_2, new_record_3])
    assert (
        records_added == 2
    ), 'Expect to write extra data to set (addition of absent data and deduplication), iteration 2'
    assert await set_db_entity_obj.contains(
        test_record.set_id, new_record_1
    ), f'Expect presence of record {new_record_1} in storage data, (added earlier), iteration 2'
    assert await set_db_entity_obj.contains(
        test_record.set_id, new_record_2
    ), f'Expect presence of record {new_record_2} in storage data, (absent data, record 2), iteration 2'
    assert await set_db_entity_obj.contains(
        test_record.set_id, new_record_3
    ), f'Expect presence of record {new_record_3} in storage data, (absent data, record 3), iteration 2'
    # modified data for iteration 2
    modified_data = SetTestData(test_record.set_id, test_record.set_data + (new_record_1, new_record_2, new_record_3))
    modified_entity_absent_data = set_db_entity_absent_data[3:]
    # checking consistency of modified set
    await check_set_consistency(set_db_entity_obj, modified_data, modified_entity_absent_data)
    # checking count of records
    await check_sets_count(set_db_entity_obj, modified_data, 0)
    # let's perform some data elimination
    modified_data = SetTestData(test_record.set_id, test_record.set_data[1:] + (new_record_1,))
    modified_entity_absent_data = set_db_entity_absent_data[1:]
    deleted_data: list[V] = set_db_entity_absent_data[1:] + [test_record.set_data[0]]
    # set_db_entity_obj.del_from_set()
    records_deleted = await set_db_entity_obj.del_from_set(modified_data.set_id, deleted_data)
    assert records_deleted == 3, 'Expect deletion of first element of test set 1 and a couple of absent data'
    await check_set_consistency(set_db_entity_obj, modified_data, modified_entity_absent_data)


async def teardown_test_set_db_entity(
    set_db_entity_test_data: list[SetTestData[K, V]],
    set_db_entity_absent_data: list[V],
    set_db_entity_obj: ISetDbEntity[K, V],
):
    for set_data in set_db_entity_test_data:
        if await set_db_entity_obj.count(set_data.set_id) > 0:
            # remove all expected set data from set
            await set_db_entity_obj.del_from_set(set_data.set_id, set_data.set_data)
            # erase all that was added from set_db_entity_absent_data
            await set_db_entity_obj.del_from_set(set_data.set_id, set_db_entity_absent_data)
            # assure that all records are eliminated
            assert await set_db_entity_obj.count(set_data.set_id) == 0, 'Unsuccessful set erasing operation'
