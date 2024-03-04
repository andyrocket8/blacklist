from datetime import datetime as dt_datetime
from enum import Enum
from ipaddress import IPv4Address
from typing import Annotated
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from .base_input_schema import now_cur_tz


class ActionType(str, Enum):
    add_action = 'add'
    remove_action = 'remove'


class UsageRecord(BaseModel):
    """Usage record for analysis and retention of old records
    Use address as a key in HKEY Redis record

    Will be removed after migration to redis stream storage
    """

    last_usage_time: Annotated[dt_datetime, Field(default_factory=now_cur_tz)]


class StreamUsageRecord(BaseModel):
    """Record for storage in stream storage (Usage record)
    We iterate over records to collect info about affected addresses
    """

    action_type: ActionType
    action_time: dt_datetime
    addresses: set[IPv4Address]


class HistoryRecordInfo(BaseModel):
    source: str
    action_time: Annotated[dt_datetime, Field(default_factory=now_cur_tz)]
    action_type: ActionType
    address_category: Optional[str] = None  # address list category (if not set then it is blacklist)
    address_group: Optional[str] = None  # address list group (if not set then it is default group)


class HistoryRecord(BaseModel):
    last_update_time: Annotated[dt_datetime, Field(default_factory=now_cur_tz)]
    history_records: Annotated[list[HistoryRecordInfo], Field(default_factory=list)]

    def sort(self):
        """Sorting the contents of history"""
        self.history_records.sort(key=lambda x: x.action_time)


class AddressHistoryRecord(HistoryRecord):
    address: IPv4Address
