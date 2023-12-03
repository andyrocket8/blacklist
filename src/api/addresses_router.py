from ipaddress import IPv4Address
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.addresses_schemas import AddResponseSchema
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import CountResponseSchema
from src.schemas.addresses_schemas import DeleteResponseSchema
from src.service.addresses_service import BlackListAddressesDBService

api_router = APIRouter()


def get_query_params(records_count: int = 10, all_records: bool = False):
    return {'records_count': records_count, 'all_records': all_records}


@api_router.get(
    '/banned',
    summary='Retrieve all blacklisted addresses from storage',
    response_model=list[IPv4Address],
)
async def get_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[dict, Depends(get_query_params)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    return await service_obj.get_records(**query_params)


@api_router.post('/banned', summary='Add blacklisted addresses to storage', response_model=AddResponseSchema)
async def save_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    added_count = await service_obj.write_records(agent_info.addresses)
    return AddResponseSchema(added=added_count)


@api_router.delete('/banned', summary='Delete blacklisted addresses from storage', response_model=DeleteResponseSchema)
async def delete_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    deleted_count = await service_obj.del_records(agent_info.addresses)
    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/banned/count', summary='Count blacklisted addresses in storage', response_model=CountResponseSchema)
async def count_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesDBService(redis_client_obj)
    count = await service_obj.count()
    return CountResponseSchema(count=count)
