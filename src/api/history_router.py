"""History handlers router"""
from ipaddress import IPv4Address
from typing import Annotated

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.usage_schemas import AddressHistoryRecord
from src.schemas.usage_schemas import HistoryRecord
from src.service.history_db_service import HistoryDBService
from src.utils.router_utils import get_query_params_with_offset

api_router = APIRouter()


@api_router.get('/', response_model=list[AddressHistoryRecord])
async def get_history(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[dict, Depends(get_query_params_with_offset)],
):
    result: list[AddressHistoryRecord] = []
    history_db_srv_obj = HistoryDBService(redis_client_obj)
    async for record, key in history_db_srv_obj.get_records(
        limit=query_params['records_count'], offset=query_params['offset']
    ):
        result.append(record)
    return result


@api_router.get('/{address_id}', response_model=HistoryRecord)
async def get_history_by_address(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)], address_id: IPv4Address
):
    history_db_srv_obj = HistoryDBService(redis_client_obj)
    history_record_obj = await history_db_srv_obj.read_record(str(address_id))
    if history_db_srv_obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'History for address {address_id} is not found')
    return history_record_obj
