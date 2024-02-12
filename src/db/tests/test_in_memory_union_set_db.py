# Testing InMemoryUnionSetDB with IPv4Address entities
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Iterable
from uuid import UUID
from uuid import uuid4

import pytest

from src.db.in_memory_set_db import InMemoryUnionSetDB


@dataclass
class FixtureSet:
    set_id: UUID
    set_base_contents: Iterable
    expected_length: int


@pytest.fixture()
def ip_addresses_data_one() -> FixtureSet:
    return FixtureSet(
        uuid4(),
        (
            IPv4Address('192.168.1.1'),
            IPv4Address('192.168.1.2'),
            IPv4Address('192.168.1.3'),
            IPv4Address('192.168.1.2'),  # some duplication
        ),
        3,
    )


@pytest.fixture()
def ip_addresses_data_two() -> FixtureSet:
    return FixtureSet(
        uuid4(),
        [
            IPv4Address('192.168.1.3'),
            IPv4Address('192.168.1.4'),
            IPv4Address('192.168.1.5'),
            IPv4Address('192.168.1.6'),
        ],
        4,
    )


@pytest.fixture()
def ip_addresses_data_three() -> FixtureSet:
    return FixtureSet(
        uuid4(),
        [
            IPv4Address('192.168.1.2'),
            IPv4Address('192.168.1.5'),
            IPv4Address('192.168.1.6'),
            IPv4Address('192.168.1.7'),
            IPv4Address('192.168.1.8'),
        ],
        5,
    )


@pytest.mark.asyncio
async def test_in_memory_db_set(ip_addresses_data_one, ip_addresses_data_two, ip_addresses_data_three):
    db_set = InMemoryUnionSetDB[UUID, IPv4Address]()
    # Check correct implementation of 'write_set' and 'count' methods for all test sets
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
    assert deleted_records == 5, 'Should be 5 deleted records'
    deleted_records = await db_set.del_from_set(
        ip_addresses_data_three.set_id, ip_addresses_data_three.set_base_contents
    )
    assert deleted_records == 0, 'Should be 0 deleted records on empty set'
