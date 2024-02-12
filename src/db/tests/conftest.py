from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import Iterable
from uuid import UUID
from uuid import uuid4

import pytest


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
