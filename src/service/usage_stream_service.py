from datetime import datetime as dt_datetime
from ipaddress import IPv4Address
from typing import Optional
from uuid import UUID

from src.core.settings import STREAM_USAGE_INFO
from src.db.base_stream_db import IStreamDb
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import ActionType
from src.schemas.usage_schemas import StreamUsageRecord


class UsageStreamAddService:
    """Service for adding records to usage stream"""

    def __init__(self, stream_id: UUID, stream_db_obj: IStreamDb[UUID, str, StreamUsageRecord]):
        self.__stream_id = stream_id
        self.__stream_db_obj = stream_db_obj

    async def add(
        self,
        action: ActionType,
        usage_info: AgentAddressesInfoWithGroup,
        address_category: Optional[str] = None,
        timestamp: Optional[dt_datetime] = None,
    ) -> str:
        """Adding data to service about address usages
        Transform this data to StreamUsageRecord and append to usages stream
        """
        saved_data = StreamUsageRecord(
            action_type=action,
            action_time=usage_info.action_time,
            addresses=set(usage_info.addresses),
            address_category=address_category,
            address_group=usage_info.address_group,
        )
        return await self.__stream_db_obj.save_by_timestamp(self.__stream_id, saved_data, timestamp=timestamp)


class UsageStreamReadService:
    """Service for reading records from usage stream"""

    def __init__(self, stream_id: UUID, stream_db_obj: IStreamDb[UUID, str, StreamUsageRecord]):
        self.__stream_id = stream_id
        self.__stream_db_obj = stream_db_obj

    async def read(
        self, start_timestamp: Optional[dt_datetime] = None, end_timestamp: Optional[dt_datetime] = None
    ) -> set[IPv4Address]:
        """Reading data about address usages. Form set with unique data"""
        result: set[IPv4Address] = set()
        async for record in self.__stream_db_obj.fetch_records(self.__stream_id, start_timestamp, end_timestamp):
            result |= record[1].addresses
        return result

    async def count(self) -> int:
        """Counting records in usage stream"""
        return await self.__stream_db_obj.count(self.__stream_id)


def get_usage_add_service(
    stream_db_obj: IStreamDb[UUID, str, StreamUsageRecord], stream_id: Optional[UUID] = None
) -> UsageStreamAddService:
    return UsageStreamAddService(STREAM_USAGE_INFO if stream_id is None else stream_id, stream_db_obj)


def get_usage_read_service(
    stream_db_obj: IStreamDb[UUID, str, StreamUsageRecord], stream_id: Optional[UUID] = None
) -> UsageStreamReadService:
    return UsageStreamReadService(STREAM_USAGE_INFO if stream_id is None else stream_id, stream_db_obj)
