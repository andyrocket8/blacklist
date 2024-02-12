# Testing InMemoryUnionSetDB with IPv4Address entities
import sys
from ipaddress import IPv4Address
from uuid import UUID

import pytest

from src.db.abstract_set_db import AbstractUnionSetDB
from src.db.in_memory_set_db import InMemoryUnionSetDB
from src.db.tests.conftest import FixtureSet


@pytest.fixture()
def db_set() -> AbstractUnionSetDB[UUID, IPv4Address]:
    return InMemoryUnionSetDB[UUID, IPv4Address]()


@pytest.mark.asyncio
async def test_abstract_union_set_db(
    db_set: AbstractUnionSetDB[UUID, IPv4Address],
    ip_addresses_data_one: FixtureSet,
    ip_addresses_data_two: FixtureSet,
    ip_addresses_data_three: FixtureSet,
):
    # Check correct implementation of 'write_set' and 'count' methods for all test sets
    try:
        for set_number, set_data in enumerate(
            (
                ip_addresses_data_one,
                ip_addresses_data_two,
                ip_addresses_data_three,
            )
        ):
            await db_set.write_to_set(set_data.set_id, set_data.set_base_contents)
            assert (
                await db_set.count(set_data.set_id) == set_data.expected_length
            ), f'Expected set length for set {set_number} is {set_data.expected_length}'
            records = [x async for x in db_set.fetch_records(set_data.set_id)]
            assert (
                len(records) == set_data.expected_length
            ), f'Expected set length for set {set_number} is {set_data.expected_length}'
        # Check validity of union function for read operation
        records = [
            x
            async for x in db_set.fetch_union_records(
                ip_addresses_data_one.set_id, ip_addresses_data_two.set_id, ip_addresses_data_three.set_id
            )
        ]
        assert len(records) == 8, 'Expected set length for union of all sets is 8'
        assert IPv4Address('192.168.1.1') in records, "Expecting existence of '192.168.1.1' address in united records"
        assert IPv4Address('192.168.1.9') not in records, "Expecting absence of '192.168.1.9' address in united records"
        # Check validity of 2 sets unions
        records = [
            x async for x in db_set.fetch_union_records(ip_addresses_data_two.set_id, ip_addresses_data_three.set_id)
        ]
        assert len(records) == 7, 'Expected set length for union of 2 sets is 7'
        assert IPv4Address('192.168.1.8') in records, "Expecting existence of '192.168.1.8' address in united records"
        assert IPv4Address('192.168.1.1') not in records, "Expecting absence of '192.168.1.1' address in united records"
        # cleaning up some sets
        deleted_records = await db_set.del_from_set(
            ip_addresses_data_three.set_id, ip_addresses_data_three.set_base_contents
        )
        records = [x async for x in db_set.fetch_union_records(ip_addresses_data_three.set_id)]
        assert len(records) == 0, 'Should be empty set contents after deletion (set 3)'
        assert (
            deleted_records == ip_addresses_data_three.expected_length
        ), f'Should be {ip_addresses_data_three.expected_length} deleted records'
        # delete from empty set
        deleted_records = await db_set.del_from_set(
            ip_addresses_data_three.set_id, ip_addresses_data_three.set_base_contents
        )
        assert deleted_records == 0, 'Should be 0 deleted records from empty set'

    finally:
        for set_number, set_data in enumerate(
            (
                ip_addresses_data_one,
                ip_addresses_data_two,
                ip_addresses_data_three,
            )
        ):
            await db_set.remove_set(set_data.set_id)
            # check set size after its deletion
            assert (
                await db_set.count(set_data.set_id) == 0
            ), f'Set on step {set_number} must be empty e.g. it is deleted!'


if __name__ == '__main__':
    pytest.main(sys.argv)
