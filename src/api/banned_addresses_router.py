from ipaddress import IPv4Address
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.service.addresses_service import AllowedAddressesDBService
from src.service.addresses_service import BlackListAddressesDBService
from src.utils.router_utils import get_query_params_with_filter

api_router = APIRouter()


@api_router.get(
    '/',
    summary='Retrieve blacklisted addresses from storage (all or partial)',
    response_model=list[IPv4Address],
)
async def get_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[dict, Depends(get_query_params_with_filter)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    banned_query_params = query_params.copy()
    del banned_query_params['filter_records']
    banned_records = await service_obj.get_records(**banned_query_params)
    if query_params['filter_records']:
        # filter by allowed IPs
        allowed_service_obj = AllowedAddressesDBService(redis_client_obj)
        allowed_records = await allowed_service_obj.get_records(all_records=True)
        return [x for x in banned_records if x not in allowed_records]
    return banned_records


@api_router.post('/', summary='Add blacklisted addresses to storage', response_model=AddResponseSchema)
async def save_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    added_count = await service_obj.write_records(agent_info.addresses)
    return AddResponseSchema(added=added_count)


@api_router.delete('/', summary='Delete blacklisted addresses from storage', response_model=DeleteResponseSchema)
async def delete_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    deleted_count = await service_obj.del_records(agent_info.addresses)
    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/count', summary='Count blacklisted addresses in storage', response_model=CountResponseSchema)
async def count_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    count = await service_obj.count()
    return CountResponseSchema(count=count)
