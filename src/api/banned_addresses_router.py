from dataclasses import asdict
from typing import Annotated
from typing import Any
from typing import AsyncGenerator
from urllib.parse import quote

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import BACKGROUND_DELETE_RECORDS
from src.core.settings import HISTORY_USAGE_INFO
from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.models.query_params_models import CommonQueryParams
from src.models.query_params_models import DownloadQueryParams
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.usage_schemas import ActionType
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.service.addresses_db_service import BlackListAddressesSetDBService
from src.service.history_db_service import HistoryDBService
from src.service.networks_db_service import AllowedNetworksSetDBService
from src.service.process_banned_ips import without_allowed_ips
from src.service.usage_db_service import UsageDBService
from src.tasks.history_update_bg_task import update_history_bg_task
from src.tasks.usage_update_bg_task import update_usage_bg_task

api_router = APIRouter()


async def get_banned_addresses(redis_client_obj: RedisAsyncio, query_params: dict[str, Any]) -> IpV4AddressList:
    service_obj = BlackListAddressesSetDBService(redis_client_obj)
    filter_records = query_params.pop('filter_records')
    banned_records = await service_obj.get_records(**query_params)
    if filter_records:
        # filter by allowed IPs
        allowed_service_obj = AllowedAddressesSetDBService(redis_client_obj)
        allowed_records = await allowed_service_obj.get_records(all_records=True)
        allowed_net_service_obj = AllowedNetworksSetDBService(redis_client_obj)
        allowed_networks = await allowed_net_service_obj.get_records(all_records=True)
        return [x async for x in without_allowed_ips(banned_records, allowed_records, allowed_networks)]
    return banned_records


@api_router.get(
    '/',
    summary='Retrieve blacklisted addresses from storage (all or partial)',
    response_model=IpV4AddressList,
)
async def banned_addresses_as_list(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[CommonQueryParams, Depends()],
):
    return await get_banned_addresses(redis_client_obj, asdict(query_params))


@api_router.post('/', summary='Add blacklisted addresses to storage', response_model=AddResponseSchema)
async def save_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    background_tasks: BackgroundTasks,
):
    service_obj = BlackListAddressesSetDBService(redis_client_obj)
    added_count = await service_obj.write_records(agent_info.addresses)
    if len(agent_info.addresses) <= BACKGROUND_DELETE_RECORDS:
        usage_db_service = UsageDBService(redis_client_obj, ACTIVE_USAGE_INFO)
        history_db_service = HistoryDBService(redis_client_obj, HISTORY_USAGE_INFO)
        # Update usage information
        background_tasks.add_task(update_usage_bg_task, usage_db_service, agent_info)
        # Update history information
        background_tasks.add_task(
            update_history_bg_task, usage_db_service, history_db_service, agent_info, ActionType.add_action
        )
    return AddResponseSchema(added=added_count)


@api_router.delete('/', summary='Delete blacklisted addresses from storage', response_model=DeleteResponseSchema)
async def delete_banned_addresses(
    agent_info: AgentAddressesInfo,
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    background_tasks: BackgroundTasks,
):
    service_obj = BlackListAddressesSetDBService(redis_client_obj)
    deleted_count = await service_obj.del_records(agent_info.addresses)
    if len(agent_info.addresses) <= BACKGROUND_DELETE_RECORDS:
        usage_db_service = UsageDBService(redis_client_obj, ACTIVE_USAGE_INFO)
        history_db_service = HistoryDBService(redis_client_obj, HISTORY_USAGE_INFO)

        background_tasks.add_task(
            update_history_bg_task, usage_db_service, history_db_service, agent_info, ActionType.remove_action
        )
    return DeleteResponseSchema(deleted=deleted_count)


@api_router.get('/count', summary='Count blacklisted addresses in storage', response_model=CountResponseSchema)
async def count_banned_addresses(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    service_obj = BlackListAddressesSetDBService(redis_client_obj)
    count = await service_obj.count()
    return CountResponseSchema(count=count)


@api_router.get('/download', summary='Get blacklisted addresses as a file')
async def banned_addresses_as_file(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[DownloadQueryParams, Depends()],
):
    async def file_records(params: dict[str, Any]) -> AsyncGenerator[str, None]:
        for record in await get_banned_addresses(redis_client_obj, params):
            yield f'{(str(record))}\n'

    headers = dict()
    query_dict_params = asdict(query_params)
    filename = query_dict_params.pop('filename')
    if filename:
        content_disposition_type = 'attachment'
        content_disposition_filename = filename
        headers['Content-Disposition'] = "{}; filename*=utf-8''{}".format(
            content_disposition_type, quote(content_disposition_filename)
        )
    return StreamingResponse(file_records(query_dict_params), media_type='text/plain', headers=headers)
