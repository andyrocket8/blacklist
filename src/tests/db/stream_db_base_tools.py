from dataclasses import dataclass
from datetime import datetime as dt_datetime

import pytest

# dataclasses for testing storage


@dataclass
class StockInfo:
    stock_name: str
    datetime: dt_datetime
    bid: float
    ask: float


@dataclass
class StockTestData:
    order: int  # order in query
    stock_data: StockInfo


@pytest.fixture
def stock_test_data() -> list[StockTestData]:
    return [
        StockTestData(
            order=2,
            stock_data=StockInfo(
                stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 2, 15), bid=90.4, ask=93.1
            ),
        ),
        StockTestData(
            order=0,
            stock_data=StockInfo(
                stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 0, 3), bid=89.1, ask=90.4
            ),
        ),
        StockTestData(
            order=1,
            stock_data=StockInfo(
                stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 1, 12), bid=88.9, ask=90.1
            ),
        ),
    ]
