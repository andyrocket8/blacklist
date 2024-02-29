import datetime
import re
from typing import Optional

from src.core.settings import CUR_TZ
from src.core.settings import HISTORY_TIMEDELTA_MASK


def get_timedelta_for_history_query(param_value: str) -> Optional[datetime.timedelta]:
    """Extract timedelta from history query param"""
    match = re.match(HISTORY_TIMEDELTA_MASK, param_value)
    if match is not None:
        time_units = int(match.group(1))
        time_unit_char = match.group(2)
        time_delta_params = {
            'days': time_units if time_unit_char == 'd' else 0,
            'hours': time_units if time_unit_char == 'h' else 0,
            'minutes': time_units if time_unit_char == 'm' else 0,
            'seconds': time_units if time_unit_char == 's' else 0,
        }
        return datetime.timedelta(**time_delta_params)
    return None


def get_current_time_with_tz() -> datetime.datetime:
    return datetime.datetime.now(tz=CUR_TZ)


def get_epoch_time() -> int:
    """Return unix epoch time in millis"""
    return int(round(datetime.datetime.now().timestamp() * 1000, 0))
