import datetime
from json import JSONEncoder
from typing import Annotated

from pydantic import BaseModel
from pydantic import Field

from .base_input_schema import now_cur_tz


class SourceRecordInfo(BaseModel):
    source: str
    last_info_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]


class UsageRecord(BaseModel):
    """Usage record for analysis and retention of old records"""

    last_usage_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
    source_records: Annotated[list[SourceRecordInfo], Field(default_factory=list)]


class HistoryRecordInfo(BaseModel):
    remover_source: str
    remove_info_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
    source_records: SourceRecordInfo


class HistoryRecord(BaseModel):
    last_update_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
    history_records: Annotated[list[HistoryRecordInfo], Field(default_factory=list)]


class DateTimeEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is datetime.datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        class_name = o.__class__.__name__
        if class_name == 'UsageRecord':
            return {'last_usage_time': o.last_usage_time, 'source_records': o.source_records}
        if class_name == 'SourceRecordInfo':
            return {'last_info_time': o.last_info_time, 'source': o.source}
        if class_name == 'HistoryRecordInfo':
            return {
                'remover_source': o.remover_source,
                'remove_info_time': o.remove_info_time,
                'source_records': o.source_records,
            }
        if class_name == 'HistoryRecord':
            return {'last_update_time': o.last_update_time, 'history_records': o.history_records}

        return JSONEncoder.default(self, o)
