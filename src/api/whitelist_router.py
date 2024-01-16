# Whitelist router
from typing import Annotated
from typing import AsyncGenerator
from urllib.parse import quote

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import StreamingResponse

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.models.query_params_models import DownloadWhitelistQueryParams
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.service.networks_db_service import AllowedNetworksSetDBService

api_router = APIRouter()


async def get_address_records(redis_client_obj: RedisAsyncio) -> AsyncGenerator[str, None]:
    """Get allowed addresses one by one for file processing"""
    address_service_obj = AllowedAddressesSetDBService(redis_client_obj)
    async for record in address_service_obj.fetch_records():
        yield f'{(str(record))}\n'


async def get_networks_records(redis_client_obj: RedisAsyncio) -> AsyncGenerator[str, None]:
    """Get allowed networks one by one for file processing"""
    network_service_obj = AllowedNetworksSetDBService(redis_client_obj)
    async for record in network_service_obj.fetch_records():
        yield f'{(str(record))}\n'


async def file_records(
    redis_client_obj: RedisAsyncio, query_params: DownloadWhitelistQueryParams
) -> AsyncGenerator[str, None]:
    counter = 0
    if query_params.with_networks:
        # fetch allowed network data
        async for record in get_networks_records(redis_client_obj):
            yield record
            counter += 1
            if not query_params.all_records and counter >= query_params.records_count:
                return  # stop iteration
    # fetch allowed addresses data
    async for record in get_address_records(redis_client_obj):
        yield record
        counter += 1
        if not query_params.all_records and counter >= query_params.records_count:
            return  # stop iteration


@api_router.get('', summary='Get whitelisted addresses as a file')
async def allowed_addresses_as_file(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[DownloadWhitelistQueryParams, Depends()],
):
    headers = dict()

    filename = query_params.filename
    if filename:
        content_disposition_type = 'attachment'
        content_disposition_filename = filename
        headers['Content-Disposition'] = "{}; filename*=utf-8''{}".format(
            content_disposition_type, quote(content_disposition_filename)
        )
    return StreamingResponse(file_records(redis_client_obj, query_params), media_type='text/plain', headers=headers)
