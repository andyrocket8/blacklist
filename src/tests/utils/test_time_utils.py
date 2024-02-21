import datetime
from dataclasses import dataclass
from typing import Optional

from pytest import fixture

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
