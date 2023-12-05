from dataclasses import asdict
from typing import Annotated
from typing import Any
from typing import AsyncGenerator
from urllib.parse import quote

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.models.query_params_models import CommonQueryParams
from src.models.query_params_models import DownloadQueryParams
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.service.addresses_db_service import AllowedAddressesDBService
from src.service.addresses_db_service import BlackListAddressesDBService
from src.service.networks_db_service import AllowedNetworksDBService
from src.service.process_banned_ips import without_allowed_ips

api_router = APIRouter()


async def get_banned_addresses(redis_client_obj: RedisAsyncio, query_params: dict[str, Any]) -> IpV4AddressList:
    service_obj = BlackListAddressesDBService(redis_client_obj)
    filter_records = query_params.pop('filter_records')
    banned_records = await service_obj.get_records(**query_params)
    if filter_records:
        # filter by allowed IPs
        allowed_service_obj = AllowedAddressesDBService(redis_client_obj)
        allowed_records = await allowed_service_obj.get_records(all_records=True)
        allowed_net_service_obj = AllowedNetworksDBService(redis_client_obj)
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
    query_params: CommonQueryParams = Depends(CommonQueryParams),
):
    return await get_banned_addresses(redis_client_obj, asdict(query_params))


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


@api_router.get('/download', summary='Get blacklisted addresses as a file')
async def banned_addresses_as_file(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: DownloadQueryParams = Depends(DownloadQueryParams),
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
