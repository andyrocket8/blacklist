import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime as dt_datetime
from typing import Generic
from typing import Type

from src.core.settings import MSK_TZ
from src.db.adapters.base_stream_db_adapter import BaseStreamDbAdapter
from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IKInternal
from src.db.base_stream_db import SKInternal
from src.models.transformation import Transformation
from src.utils.time_utils import decode_datetime
from src.utils.time_utils import encode_datetime

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


class JsonStockInfoEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, StockInfo):
            return asdict(o)
        if type(o) is dt_datetime:
            return encode_datetime(o)
        return super().default(o)


class StockInfoTransformer(Transformation[StockInfo, bytes]):

    @classmethod
    def transform_to_storage(cls, value: StockInfo) -> bytes:
        return json.dumps(value, cls=JsonStockInfoEncoder).encode()

    @classmethod
    def transform_from_storage(cls, value: bytes) -> StockInfo:
        loaded = json.loads(value)
        loaded['datetime'] = decode_datetime(loaded['datetime'])
        return StockInfo(**loaded)


def test_stock_info_transformer():
    stock_info_no_tz = StockInfo(
        stock_name='Total Securities Inc', datetime=dt_datetime(2023, 12, 1, 18, 2, 15), bid=90.4, ask=93.1
    )
    stock_info_no_tz_bytes = StockInfoTransformer.transform_to_storage(stock_info_no_tz)
    assert type(stock_info_no_tz_bytes) is bytes, 'Wrong transformation from StockInfo without TZ to bytes'
    assert (
        StockInfoTransformer.transform_from_storage(stock_info_no_tz_bytes) == stock_info_no_tz
    ), 'Stock info without timezone info has been faulty transformed'

    stock_info_with_tz = StockInfo(
        stock_name='Total Securities Inc',
        datetime=dt_datetime(2023, 12, 1, 18, 2, 15, tzinfo=MSK_TZ),
        bid=90.4,
        ask=93.1,
    )
    stock_info_with_tz_bytes = StockInfoTransformer.transform_to_storage(stock_info_with_tz)
    assert type(stock_info_with_tz_bytes) is bytes, 'Wrong transformation from StockInfo with TZ to bytes'
    assert StockInfoTransformer.transform_from_storage(stock_info_with_tz_bytes).datetime == stock_info_with_tz.datetime
    assert (
        StockInfoTransformer.transform_from_storage(stock_info_with_tz_bytes) == stock_info_with_tz
    ), 'Stock info with timezone info has been faulty transformed'


class StockInfoStreamAdapter(
    BaseStreamDbAdapter[IK, SK, StockInfo, IKInternal, SKInternal, bytes], Generic[IK, SK, IKInternal, SKInternal]
):
    """Base adapter with defined entity transformation"""

    value_transformer: Type[Transformation[StockInfo, bytes]] = StockInfoTransformer
