# utilities for testing set db classes and adapters
from typing import Callable

from src.db.base_set_db import ISetDb
from src.db.base_set_db_entity import ISetDbEntity
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V

from .set_db_entity_base_tools import add_records_to_sets
from .set_db_entity_base_tools import check_set_consistency
from .test_set_db_classes import SetTestData


async def run_test_set_db(
    set_db_entity_test_data: list[SetTestData[K, V]],
    set_db_entity_obj: ISetDbEntity[K, V],
    set_db_obj: ISetDb[K],
    set_identity_factory: Callable[[], K],
):
    """Run the test with set db
    Scenario:
    1) Check existence of empty sets
    2) Try to delete empty sets and copy data from empty set
    3) Add data to sets
    4) Try to manipulate data, checking consistency
    5) Try to delete sets, checking related functions for ISetDb and ISetDbEntity

    """
    # obtain random empty set identity
    nonexistent_set_id: K = set_identity_factory()
    # checking existence of empty set
    assert not await set_db_obj.exists(nonexistent_set_id), 'Error result on checking existence of nonexistent set'
    # checking deletion of empty set
    assert (
        await set_db_obj.del_set(nonexistent_set_id) == 0
    ), '0 should returned on attempt of deletion of nonexistent set'
    # add some data to storage
    await add_records_to_sets(set_db_entity_obj, set_db_entity_test_data)
    for set_data in set_db_entity_test_data:
        assert await set_db_obj.exists(set_data.set_id), 'Error result on checking existence of created set'
    # checking copy operation
    copied_set_id: K = set_identity_factory()
    sets_copied = await set_db_obj.copy_set(set_db_entity_test_data[1].set_id, copied_set_id)
    assert sets_copied == 1, 'Expect 1 copied set'
    # checking set consistency
    await check_set_consistency(set_db_entity_obj, set_db_entity_test_data[1], list())
    copied_set_data = SetTestData(copied_set_id, set_db_entity_test_data[1].set_data)
    await check_set_consistency(set_db_entity_obj, copied_set_data, list())
    # noop copy operation
    sets_copied = await set_db_obj.copy_set(set_db_entity_test_data[1].set_id, copied_set_id)
    assert sets_copied == 0, 'Expect no copies made'
    # checking consistency
    await check_set_consistency(set_db_entity_obj, copied_set_data, list())
    # clear some data from copied set
    records_deleted = await set_db_entity_obj.del_from_set(copied_set_id, (copied_set_data.set_data[0],))
    assert records_deleted == 1, 'Expected some clean operations'
    # checking consistency without first
    await check_set_consistency(set_db_entity_obj, SetTestData(copied_set_id, copied_set_data.set_data[1:]), list())
    # overwrite copy operation
    sets_copied = await set_db_obj.copy_set(set_db_entity_test_data[0].set_id, copied_set_id, True)
    assert sets_copied == 1, 'Expect new copy with overwrite'
    # checking consistency
    copied_set_data = SetTestData(copied_set_id, set_db_entity_test_data[0].set_data)
    await check_set_consistency(set_db_entity_obj, copied_set_data, list())


async def teardown_test_set_db(
    set_db_entity_test_data: list[SetTestData[K, V]],
    set_db_obj: ISetDb[K],
):
    for set_data in set_db_entity_test_data:
        await set_db_obj.del_set(set_data.set_id)
