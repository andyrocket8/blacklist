from ipaddress import IPv4Address
from typing import Annotated

from fastapi import APIRouter, Depends

from src.db.redis_db import RedisAsyncio, redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo

api_router = APIRouter()


@api_router.get(
    '/addresses',
    summary='Retrieve all blacklisted addresses from storage',
    response_model=list[IPv4Address],
)
async def get_addresses():
    return []


@api_router.post('/addresses', summary='Add blacklisted addresses to storage')
async def set_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    await redis_client_obj.ping()
    pass
