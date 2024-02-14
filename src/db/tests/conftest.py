from dataclasses import dataclass
from datetime import date as dt_date
from ipaddress import IPv4Address
from typing import Iterable
from uuid import UUID
from uuid import uuid4

import pytest

from .test_set_db_classes import Car
from .test_set_db_classes import SetTestData


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


@pytest.fixture()
def car_set_test_data() -> list[SetTestData[UUID, Car]]:
    return [
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


@pytest.fixture()
def car_set_absent_test_data() -> list[Car]:
    return [
        Car('Honda', 'Pilot', 'Dark grey', dt_date(2013, 8, 15), 'X003XX99'),
        Car('Renault', 'Duster', 'White', dt_date(2021, 2, 1), 'B785AX77'),
        Car('Toyota', 'RAV4', 'Blue', dt_date(2021, 7, 7), 'K223KK190'),
        Car('Toyota', 'Prius', 'Grey (as most of them)', dt_date(2018, 1, 31), 'P300KK23'),
        Car('VAZ', '21099', 'Rusty', dt_date(1996, 12, 31), 'M100MX77'),
    ]
