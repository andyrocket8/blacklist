import datetime
from enum import Enum
from ipaddress import IPv4Address
from json import JSONEncoder
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
    """

    last_usage_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]


class HistoryRecordInfo(BaseModel):
    source: str
    action_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
    action_type: ActionType
    address_category: Optional[str] = None  # address list category (if not set then it is blacklist)
    address_group: Optional[str] = None  # address list group (if not set then it is default group)


class HistoryRecord(BaseModel):
    last_update_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
    history_records: Annotated[list[HistoryRecordInfo], Field(default_factory=list)]

    def sort(self):
        """Sorting the contents of history"""
        self.history_records.sort(key=lambda x: x.action_time)


class AddressHistoryRecord(HistoryRecord):
    address: IPv4Address


class UsageClassesEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is datetime.datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        class_name = o.__class__.__name__
        if class_name == 'UsageRecord':
            return o.model_dump(mode='json')
        if class_name == 'HistoryRecordInfo':
            return o.model_dump(mode='json')
        if class_name == 'HistoryRecord':
            return o.model_dump(mode='json')
        if class_name == 'AddressHistoryRecord':
            return o.model_dump(mode='json')

        return JSONEncoder.default(self, o)
