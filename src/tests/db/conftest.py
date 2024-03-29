import logging
import random
from dataclasses import dataclass
from datetime import date as dt_date
from datetime import datetime as dt_datetime
from datetime import timedelta
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import Generator
from typing import Iterable
from uuid import UUID
from uuid import uuid4

import pytest

from src.db.storages.redis_db_pool import RedisConnectionPool

from .classes_for_hash_db_test import AddressInfo
from .classes_for_hash_db_test import HostInfo
from .classes_for_hash_db_test import NetworkInfo
from .classes_for_set_db_test import Car
from .classes_for_set_db_test import SetTestData
from .classes_for_stream_db_test import CheckFilterData
from .classes_for_stream_db_test import StockInfo
from .classes_for_stream_db_test import StocksTestDataSet
from .classes_for_stream_db_test import StockTestData

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s [%(name)s] %(message)s')


@dataclass
class FixtureSet:
    set_id: UUID
    set_base_contents: Iterable
    expected_length: int


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
def car_set_test_data() -> list[SetTestData[UUID, Car]]:
    # All data in this set is faked
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


@pytest.fixture
def car_set_absent_test_data() -> list[Car]:
    # All data in this set is faked
    return [
        Car('Honda', 'Pilot', 'Dark grey', dt_date(2013, 8, 15), 'X003XX99'),
        Car('Renault', 'Duster', 'White', dt_date(2021, 2, 1), 'B785AX77'),
        Car('Toyota', 'RAV4', 'Blue', dt_date(2021, 7, 7), 'K223KK190'),
        Car('Toyota', 'Prius', 'Grey (as most of them)', dt_date(2018, 1, 31), 'P300KK23'),
        Car('VAZ', '21099', 'Rusty', dt_date(1996, 12, 31), 'M100MX77'),
    ]


# Fixtures for Hash DB tests


def generate_signature() -> bytes:
    return random.randbytes(125)


# Test assume the hash storage of networks with IP addresses as keys and HostInfo instances as values
@pytest.fixture
def company_network_info_for_test() -> list[NetworkInfo]:
    result: list[NetworkInfo] = list()
    # All data in this set is faked
    # Network 1 (Head office somewhere in Texas)
    result.append(
        NetworkInfo(
            network=IPv4Network('192.168.1.0/24'),
            hosts=[
                AddressInfo(
                    address=IPv4Address('192.168.1.1'),
                    host_info=HostInfo(
                        host_name='ho-router-01',
                        host_description='Head office main router',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('192.168.1.2'),
                    host_info=HostInfo(
                        host_name='ho-server-01',
                        host_description='Head office file server',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('192.168.1.30'),
                    host_info=HostInfo(
                        host_name='ho-host-01', host_description='John Smith computer', signature=generate_signature()
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('192.168.1.31'),
                    host_info=HostInfo(
                        host_name='ho-host-02',
                        host_description='Barbara Thompson computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('192.168.1.32'),
                    host_info=HostInfo(
                        host_name='ho-host-03', host_description='Kate Evans computer', signature=generate_signature()
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('192.168.1.33'),
                    host_info=HostInfo(
                        host_name='ho-host-04',
                        host_description='Luke Skywalker notebook',
                        signature=generate_signature(),
                    ),
                ),
            ],
        )
    )
    # Network 2 (New York branch)
    result.append(
        NetworkInfo(
            network=IPv4Network('10.100.1.0/24'),
            hosts=[
                AddressInfo(
                    address=IPv4Address('10.100.1.1'),
                    host_info=HostInfo(
                        host_name='br-01-router-01',
                        host_description='New York Branch main router',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.1.2'),
                    host_info=HostInfo(
                        host_name='br-01-server-01',
                        host_description='New York Branch file server',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.1.3'),
                    host_info=HostInfo(
                        host_name='br-01-server-02',
                        host_description='New York ERP system server',
                        signature=generate_signature(),
                    ),
                ),
                # some awesome staff here
                AddressInfo(
                    address=IPv4Address('10.100.1.10'),
                    host_info=HostInfo(
                        host_name='br-01-printer-01',
                        host_description='New York laser printer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.1.30'),
                    host_info=HostInfo(
                        host_name='br-01-host-01',
                        host_description='Mark Navarro computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.1.31'),
                    host_info=HostInfo(
                        host_name='br-01-host-02',
                        host_description='Jane Wilson computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.1.32'),
                    host_info=HostInfo(
                        host_name='br-01-host-03',
                        host_description='Our boss playstation',
                        signature=generate_signature(),
                    ),
                ),
            ],
        )
    )
    # Network 3 (Arizona Branch)
    result.append(
        NetworkInfo(
            network=IPv4Network('10.100.2.0/24'),
            hosts=[
                AddressInfo(
                    address=IPv4Address('10.100.2.1'),
                    host_info=HostInfo(
                        host_name='br-02-router-01',
                        host_description='Arizona Branch main router',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.2'),
                    host_info=HostInfo(
                        host_name='br-02-server-01',
                        host_description='Arizona Branch file server',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.3'),
                    host_info=HostInfo(
                        host_name='br-02-server-02',
                        host_description='Arizona Branch web application server',
                        signature=generate_signature(),
                    ),
                ),
                # Network addresses. Some mess from our devops!
                AddressInfo(
                    address=IPv4Address('10.100.2.50'),
                    host_info=HostInfo(
                        host_name='br-03-host-01',
                        host_description='Will Ericssen computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.52'),
                    host_info=HostInfo(
                        host_name='br-03-host-03',
                        host_description='Sandra Bones computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.54'),
                    host_info=HostInfo(
                        host_name='br-03-host-05',
                        host_description='Craig Sommer computer',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.56'),
                    host_info=HostInfo(
                        host_name='br-03-host-12',
                        host_description='Dave Bronco notebook',
                        signature=generate_signature(),
                    ),
                ),
                AddressInfo(
                    address=IPv4Address('10.100.2.127'),
                    host_info=HostInfo(
                        host_name='br-03-phone-01',
                        host_description='Dave Bronco iPad',
                        signature=generate_signature(),
                    ),
                ),
            ],
        )
    )
    return result


@pytest.fixture(scope='module')
def redis_connection_pool(redis_env_for_test) -> Generator[RedisConnectionPool, None, None]:
    """Yield connection pool if redis test env is up"""
    if not redis_env_for_test.test_redis_available:
        pytest.skip('No redis configuration file detected!')
    print(f'Redis config now: {redis_env_for_test}')
    yield RedisConnectionPool(redis_env_for_test.redis_config)


# Union set test data
@pytest.fixture
def union_set_test_data() -> list[SetTestData[UUID, int]]:
    return [
        SetTestData[UUID, int](
            set_id=uuid4(),
            set_data=(
                1,
                2,
                3,
                4,
                5,
                4,
                5,
            ),
        ),
        SetTestData[UUID, int](
            set_id=uuid4(),
            set_data=(
                6,
                7,
            ),
        ),
        SetTestData[UUID, int](
            set_id=uuid4(),
            set_data=(
                5,
                6,
                7,
                8,
                9,
            ),
        ),
        SetTestData[UUID, int](
            set_id=uuid4(),
            set_data=(5, 6, 7, 8, 9, 10),
        ),
    ]


ZERO_ORDER_STOCK_INFO_RECORD = StockTestData(
    order=0,
    stock_data=StockInfo(
        stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 0, 3, 101000), bid=89.1, ask=90.4
    ),
)

FIRST_ORDER_STOCK_INFO_RECORD = StockTestData(
    order=1,
    stock_data=StockInfo(
        stock_name='Extra Brewery Co', datetime=dt_datetime(2023, 12, 1, 18, 0, 3, 101000), bid=16.12, ask=16.42
    ),
)

SECOND_ORDER_STOCK_INFO_RECORD = StockTestData(
    order=2,
    stock_data=StockInfo(
        stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 1, 12), bid=88.9, ask=90.1
    ),
)

THIRD_ORDER_STOCK_INFO_RECORD = StockTestData(
    order=3,
    stock_data=StockInfo(
        stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 2, 15), bid=90.4, ask=93.1
    ),
)

FOURTH_ORDER_STOCK_INFO_RECORD = StockTestData(
    order=4,
    stock_data=StockInfo(
        stock_name='Extra Brewery Co', datetime=dt_datetime(2024, 2, 1, 12, 23, 1), bid=18.2, ask=21.3
    ),
)


@pytest.fixture
def stocks_test_data() -> list[StockTestData]:
    return [
        FOURTH_ORDER_STOCK_INFO_RECORD,  # should be last on in sorted output
        THIRD_ORDER_STOCK_INFO_RECORD,
        ZERO_ORDER_STOCK_INFO_RECORD,  # should be first on in sorted output
        FIRST_ORDER_STOCK_INFO_RECORD,
        SECOND_ORDER_STOCK_INFO_RECORD,
    ]


@pytest.fixture
def stocks_set_test_data(stocks_test_data: list[StockTestData]) -> StocksTestDataSet:
    return StocksTestDataSet(
        stocks_test_data,
        [
            # all records with no filtering
            CheckFilterData(
                start_date=None,
                end_date=None,
                expected_records_count=5,
                expected_first_record=ZERO_ORDER_STOCK_INFO_RECORD,
                expected_last_record=FOURTH_ORDER_STOCK_INFO_RECORD,
            ),
            # all records with the first two records with the same time
            CheckFilterData(
                start_date=ZERO_ORDER_STOCK_INFO_RECORD.stock_data.datetime,
                end_date=None,
                expected_records_count=5,
                expected_first_record=ZERO_ORDER_STOCK_INFO_RECORD,
                expected_last_record=FOURTH_ORDER_STOCK_INFO_RECORD,
            ),
            # all records without first two records with the same time
            CheckFilterData(
                start_date=ZERO_ORDER_STOCK_INFO_RECORD.stock_data.datetime + timedelta(seconds=1),
                end_date=None,
                expected_records_count=3,
                expected_first_record=SECOND_ORDER_STOCK_INFO_RECORD,
                expected_last_record=FOURTH_ORDER_STOCK_INFO_RECORD,
            ),
            # two sides bound search with the inclusion oin the end of search
            CheckFilterData(
                start_date=ZERO_ORDER_STOCK_INFO_RECORD.stock_data.datetime + timedelta(seconds=1),
                end_date=FOURTH_ORDER_STOCK_INFO_RECORD.stock_data.datetime,
                expected_records_count=3,
                expected_first_record=SECOND_ORDER_STOCK_INFO_RECORD,
                expected_last_record=FOURTH_ORDER_STOCK_INFO_RECORD,
            ),
            # two sides bound search
            CheckFilterData(
                start_date=ZERO_ORDER_STOCK_INFO_RECORD.stock_data.datetime + timedelta(seconds=1),
                end_date=FOURTH_ORDER_STOCK_INFO_RECORD.stock_data.datetime - timedelta(seconds=1),
                expected_records_count=2,
                expected_first_record=SECOND_ORDER_STOCK_INFO_RECORD,
                expected_last_record=THIRD_ORDER_STOCK_INFO_RECORD,
            ),
            CheckFilterData(
                start_date=None,
                end_date=THIRD_ORDER_STOCK_INFO_RECORD.stock_data.datetime - timedelta(seconds=1),
                expected_records_count=3,
                expected_first_record=ZERO_ORDER_STOCK_INFO_RECORD,
                expected_last_record=SECOND_ORDER_STOCK_INFO_RECORD,
            ),
        ],
    )
