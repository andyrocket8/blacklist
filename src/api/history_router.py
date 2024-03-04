"""History handlers router"""

import datetime
from ipaddress import IPv4Address
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from src.api.di.db_di_routines import get_stream_db_adapter
from src.db.base_stream_db import IStreamDb
from src.db.storages.redis_db import RedisAsyncio
from src.db.storages.redis_db import redis_client
from src.models.query_params_models import HistoryQueryParams
from src.schemas.base_input_schema import now_cur_tz
from src.schemas.usage_schemas import AddressHistoryRecord
from src.schemas.usage_schemas import HistoryRecord
from src.schemas.usage_schemas import StreamUsageRecord
from src.service.history_db_service import HistoryDBService
from src.service.usage_stream_service import UsageStreamReadService
from src.service.usage_stream_service import get_usage_read_service
from src.utils.time_utils import get_current_time_with_tz
from src.utils.time_utils import get_timedelta_for_history_query

api_router = APIRouter()


@api_router.get('', response_model=list[AddressHistoryRecord])
async def get_history(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[HistoryQueryParams, Depends()],
):
    result: list[AddressHistoryRecord] = []
    history_db_srv_obj = HistoryDBService(redis_client_obj)
    current_time = now_cur_tz()
    all_records = query_params.all_records
    offset_timedelta = get_timedelta_for_history_query(query_params.time_offset)
    if not all_records and offset_timedelta is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong value for "time_offset" parameter')
    board_time = current_time - (offset_timedelta if offset_timedelta is not None else datetime.timedelta(seconds=0))
    async for record, key in history_db_srv_obj.get_records(limit=0, offset=0):
        if all_records or record.last_update_time >= board_time:
            result.append(record)
    return result


@api_router.get('/addresses', response_model=list[IPv4Address])
async def get_usage_addresses(
    usage_read_db_service: Annotated[IStreamDb[UUID, str, StreamUsageRecord], Depends(get_stream_db_adapter)],
    query_params: Annotated[HistoryQueryParams, Depends()],
):
    """Getting list of changed addresses in time period"""
    read_service_obj: UsageStreamReadService = get_usage_read_service(usage_read_db_service)
    all_records = query_params.all_records
    offset_timedelta = get_timedelta_for_history_query(query_params.time_offset)
    start_time = (
        (get_current_time_with_tz() - offset_timedelta) if (offset_timedelta is not None and not all_records) else None
    )
    result = await read_service_obj.read(start_timestamp=start_time)
    return sorted(list(result))


@api_router.get('/{ip_address}', response_model=HistoryRecord)
async def get_history_by_address(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)], ip_address: IPv4Address
):
    history_db_srv_obj = HistoryDBService(redis_client_obj)
    history_record_obj = await history_db_srv_obj.read_record(str(ip_address))
    if history_record_obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'History for address {ip_address} is not found')
    return history_record_obj
