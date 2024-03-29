from typing import Annotated
from typing import Callable
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpNetwork
from src.db.storages.redis_db import RedisAsyncio
from src.db.storages.redis_db import redis_client
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.network_schemas import AgentNetworkInfo
from src.schemas.network_schemas import IPv4NetworkList
from src.service.networks_db_service import AllowedNetworksSetDBEntityService
from src.utils.router_utils import get_query_params

from .http_auth_wrapper import get_proc_auth_checker

api_router = APIRouter()
allowed_networks_auth_check: Callable = get_proc_auth_checker(need_admin_permission=False)


@api_router.get(
    '',
    summary='Retrieve allowed networks from storage (all or partial)',
    response_model=IPv4NetworkList,
)
async def get_allowed_networks(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[dict, Depends(get_query_params)],
):
    service_obj = AllowedNetworksSetDBEntityService(
        SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(redis_client_obj))
    )
    return [x async for x in service_obj.fetch_records(**query_params)]


@api_router.post('/add', summary='Add allowed networks to storage', response_model=AddResponseSchema)
async def save_allowed_networks(
    agent_info: AgentNetworkInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    auth: Optional[HTTPAuthorizationCredentials] = Depends(allowed_networks_auth_check),  # noqa: B008
):
    service_obj = AllowedNetworksSetDBEntityService(
        SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(redis_client_obj))
    )
    added_count = await service_obj.write_records(agent_info.networks)
    return AddResponseSchema(added=added_count)


@api_router.post('/delete', summary='Delete allowed networks from storage', response_model=DeleteResponseSchema)
async def delete_allowed_networks(
    agent_info: AgentNetworkInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    auth: Optional[HTTPAuthorizationCredentials] = Depends(allowed_networks_auth_check),  # noqa: B008
):
    service_obj = AllowedNetworksSetDBEntityService(
        SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(redis_client_obj))
    )
    deleted_count = await service_obj.del_records(agent_info.networks)
    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/count', summary='Count allowed networks in storage', response_model=CountResponseSchema)
async def count_allowed_networks(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = AllowedNetworksSetDBEntityService(
        SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(redis_client_obj))
    )
    count = await service_obj.count()
    return CountResponseSchema(count=count)
