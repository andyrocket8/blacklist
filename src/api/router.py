from ipaddress import IPv4Address
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.service.addresses_service import AddressesDBService

api_router = APIRouter()


@api_router.get(
    '/addresses',
    summary='Retrieve all blacklisted addresses from storage',
    response_model=list[IPv4Address],
)
async def get_addresses(redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)]):
    service_obj = AddressesDBService(redis_client_obj)
    return await service_obj.get_records()


@api_router.post('/addresses', summary='Add blacklisted addresses to storage')
async def set_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = AddressesDBService(redis_client_obj)
    await service_obj.write_records(agent_info.addresses)
