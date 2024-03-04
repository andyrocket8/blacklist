import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime as dt_datetime
from typing import Generic
from typing import Optional
from typing import Type

from src.core.settings import MSK_TZ
from src.db.adapters.base_stream_db_adapter import BaseStreamDbAdapter
from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IKInternal
from src.db.base_stream_db import SKInternal
from src.models.transformation import Transformation
from src.models.transformation import TransformOneToOne
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


class StockInfoDictTransformer(Transformation[StockInfo, dict[str, str]]):

    @classmethod
    def transform_to_storage(cls, value: StockInfo) -> dict[str, str]:
        return {
            'stock_name': value.stock_name,
            'datetime': encode_datetime(value.datetime),
            'bid': str(value.bid),
            'ask': str(value.ask),
        }

    @classmethod
    def transform_from_storage(cls, value: dict[str, str]) -> StockInfo:
        return StockInfo(
            stock_name=value['stock_name'],
            datetime=decode_datetime(value['datetime']),
            bid=float(value['bid']),
            ask=float(value['ask']),
        )


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


class StockInfoIntStrStreamAdapter(StockInfoStreamAdapter[int, str, int, str]):
    """Adapter with int as set identifiers and str as timestamp keys"""

    stream_key_transformer: Type[Transformation[int, int]] = TransformOneToOne[int]
    ts_transformer: Type[Transformation[str, str]] = TransformOneToOne[str]


class TransformIntToStr(Transformation[int, str]):

    @classmethod
    def transform_to_storage(cls, value: int) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> int:
        return int(value)


class StockInfoDictStreamAdapter(BaseStreamDbAdapter[int, str, StockInfo, str, str, dict[str, str]]):
    """Adapter for transforming
    - int to str for stream id
    - str to str for stream timestamp keys
    - StockInfo into dict[str, bytes] for entities
    """

    stream_key_transformer: Type[Transformation[int, str]] = TransformIntToStr
    ts_transformer: Type[Transformation[str, str]] = TransformOneToOne[str]
    value_transformer: Type[Transformation[StockInfo, dict[str, str]]] = StockInfoDictTransformer


@dataclass
class CheckFilterData:
    start_date: Optional[dt_datetime]
    end_date: Optional[dt_datetime]
    expected_records_count: int
    expected_first_record: StockTestData
    expected_last_record: StockTestData


@dataclass
class StocksTestDataSet:
    stock_test_list: list[StockTestData]
    check_filter_data_list: list[CheckFilterData]  # some sets for checking filtering
