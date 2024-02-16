from typing import Annotated
from typing import Callable
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.storages.redis_db import RedisAsyncio
from src.db.storages.redis_db import redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.utils.router_utils import get_query_params

from .http_auth_wrapper import get_proc_auth_checker

api_router = APIRouter()

allowed_addresses_auth_check: Callable = get_proc_auth_checker(need_admin_permission=False)


@api_router.get(
    '',
    summary='Retrieve allowed addresses from storage (all or partial)',
    response_model=IpV4AddressList,
)
async def get_allowed_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[dict, Depends(get_query_params)],
):
    service_obj = AllowedAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    return await service_obj.get_records(**query_params)


@api_router.post('/add', summary='Add allowed addresses to storage', response_model=AddResponseSchema)
async def save_allowed_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    auth: Optional[HTTPAuthorizationCredentials] = Depends(allowed_addresses_auth_check),  # noqa: B008
):
    service_obj = AllowedAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    added_count = await service_obj.write_records(agent_info.addresses)
    return AddResponseSchema(added=added_count)


@api_router.post('/delete', summary='Delete allowed addresses from storage', response_model=DeleteResponseSchema)
async def delete_allowed_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    auth: Optional[HTTPAuthorizationCredentials] = Depends(allowed_addresses_auth_check),  # noqa: B008
):
    service_obj = AllowedAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    deleted_count = await service_obj.del_records(agent_info.addresses)
    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/count', summary='Count allowed addresses in storage', response_model=CountResponseSchema)
async def count_allowed_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = AllowedAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    count = await service_obj.count()
    return CountResponseSchema(count=count)
