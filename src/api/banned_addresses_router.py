import datetime
import logging
from dataclasses import asdict
from typing import Annotated
from typing import Any
from typing import Optional

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import BACKGROUND_ADD_RECORDS
from src.core.settings import BACKGROUND_DELETE_RECORDS
from src.core.settings import HISTORY_USAGE_INFO
from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.db.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.set_db_entity_str_adapter import SetDbEntityStrAdapterIpNetwork
from src.models.query_params_models import CommonQueryParams
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.usage_schemas import ActionType
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.service.addresses_db_service import BlackListAddressesSetDBService
from src.service.networks_db_service import AllowedNetworksSetDBService
from src.service.process_banned_ips import without_allowed_ips
from src.tasks.celery_tasks import celery_update_history_task
from src.tasks.celery_tasks import celery_update_usage_info_task
from src.tasks.history_update_bg_task import update_history_bg_task_ns
from src.tasks.usage_update_bg_task import update_usage_bg_task_ns

from .http_auth_wrapper import get_proc_auth_checker

api_router = APIRouter()
banned_addresses_auth_check = get_proc_auth_checker(need_admin_permission=False)


async def get_banned_addresses(redis_client_obj: RedisAsyncio, query_params: dict[str, Any]) -> IpV4AddressList:
    # TODO transform fetching logic to generator
    start_moment = datetime.datetime.now()
    try:
        logging.debug('Starting blacklist query execution')
        service_obj = BlackListAddressesSetDBService(
            SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
        )
        filter_records = query_params.pop('filter_records')
        # TODO There's no need to get all records. We can fetch them for further filtering and return them without
        # memory utilization and get the right records count
        # At the moment some records might be truncated with following filtering
        banned_records = await service_obj.get_records(**query_params)
        if filter_records:
            # filter by allowed IPs
            allowed_service_obj = AllowedAddressesSetDBService(
                SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
            )
            allowed_records = await allowed_service_obj.get_records(all_records=True)
            allowed_net_service_obj = AllowedNetworksSetDBService(
                SetDbEntityStrAdapterIpNetwork(RedisSetDbEntityAdapter(redis_client_obj))
            )
            allowed_networks = await allowed_net_service_obj.get_records(all_records=True)
            return [x async for x in without_allowed_ips(banned_records, allowed_records, allowed_networks)]
        return banned_records
    finally:
        duration = datetime.datetime.now() - start_moment
        logging.debug(
            'Finished blacklist query execution, elapsed %s milliseconds',
            duration.seconds + duration.microseconds / 1000,
        )


@api_router.get(
    '',
    summary='Retrieve blacklisted addresses from storage (all or partial)',
    response_model=IpV4AddressList,
)
async def banned_addresses_as_list(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[CommonQueryParams, Depends()],
):
    return await get_banned_addresses(redis_client_obj, asdict(query_params))


@api_router.post('/add', summary='Add blacklisted addresses to storage', response_model=AddResponseSchema)
async def save_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    background_tasks: BackgroundTasks,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(banned_addresses_auth_check),  # noqa: B008
):
    service_obj = BlackListAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    added_count = await service_obj.write_records(agent_info.addresses)
    if len(agent_info.addresses) <= BACKGROUND_ADD_RECORDS:
        # run fast tasks in background
        # Update usage information
        background_tasks.add_task(update_usage_bg_task_ns, ACTIVE_USAGE_INFO, agent_info)
        # Update history information
        background_tasks.add_task(
            update_history_bg_task_ns, ACTIVE_USAGE_INFO, HISTORY_USAGE_INFO, agent_info, ActionType.add_action
        )
    else:
        # invoke celery task for update usage and history
        agent_info_dict = agent_info.encode()
        celery_update_usage_info_task.apply_async((agent_info_dict,))
        celery_update_history_task.apply_async(
            (
                agent_info_dict,
                ActionType.add_action,
            )
        )

    return AddResponseSchema(added=added_count)


@api_router.post('/delete', summary='Delete blacklisted addresses from storage', response_model=DeleteResponseSchema)
async def delete_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    background_tasks: BackgroundTasks,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(banned_addresses_auth_check),  # noqa: B008
):
    service_obj = BlackListAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    deleted_count = await service_obj.del_records(agent_info.addresses)
    if len(agent_info.addresses) <= BACKGROUND_DELETE_RECORDS:
        background_tasks.add_task(
            update_history_bg_task_ns, ACTIVE_USAGE_INFO, HISTORY_USAGE_INFO, agent_info, ActionType.remove_action
        )
    else:
        # invoke celery task for update usage
        agent_info_dict = agent_info.encode()
        celery_update_history_task.apply_async(agent_info_dict, ActionType.remove_action)

    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/count', summary='Count blacklisted addresses in storage', response_model=CountResponseSchema)
async def count_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesSetDBService(
        SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
    )
    count = await service_obj.count()
    return CountResponseSchema(count=count)
