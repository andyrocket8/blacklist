import datetime
from dataclasses import dataclass
from typing import Optional
from zoneinfo import ZoneInfo

from pytest import fixture

from src.utils.time_utils import decode_datetime
from src.utils.time_utils import encode_datetime
from src.utils.time_utils import get_timedelta_for_history_query


@dataclass
class TimedeltaFixture:
    source: str
    target: Optional[datetime.timedelta]


@fixture
def fixture_data() -> list[TimedeltaFixture]:
    return [
        TimedeltaFixture(source='1m', target=datetime.timedelta(minutes=1)),
        TimedeltaFixture(source='10m', target=datetime.timedelta(minutes=10)),
        TimedeltaFixture(source=' 10m', target=None),
        TimedeltaFixture(source='1000s', target=datetime.timedelta(seconds=1000)),
        TimedeltaFixture(source='33h', target=datetime.timedelta(hours=33)),
        TimedeltaFixture(source='365d', target=datetime.timedelta(days=365)),
    ]


def test_timedelta_func(fixture_data: list[TimedeltaFixture]):
    for test_record in fixture_data:
        assert test_record.target == get_timedelta_for_history_query(test_record.source)


def test_encoding_and_decoding():
    curr_date_time = datetime.datetime.now()
    encoded_str: str = encode_datetime(curr_date_time)
    assert curr_date_time == decode_datetime(encoded_str), 'Encode-decode operation (no tz) is not successful'
    curr_date_time_tz = datetime.datetime.now(tz=ZoneInfo('Europe/Moscow'))
    encoded_str_tz: str = encode_datetime(curr_date_time_tz)
    assert curr_date_time_tz == decode_datetime(encoded_str_tz), 'Encode-decode operation (Msk tz) is not successful'
    curr_date_time_utc = datetime.datetime.now(tz=ZoneInfo('UTC'))
    encoded_str_utc: str = encode_datetime(curr_date_time_utc)
    assert curr_date_time_utc == decode_datetime(encoded_str_utc), 'Encode-decode operation (UTC tz) is not successful'
