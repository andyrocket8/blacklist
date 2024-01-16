# Blacklist router
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
from src.models.query_params_models import DownloadBlackListQueryParams

from .banned_addresses_router import get_banned_addresses

api_router = APIRouter()


@api_router.get('', summary='Get blacklisted addresses as a file')
async def banned_addresses_as_file(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    query_params: Annotated[DownloadBlackListQueryParams, Depends()],
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
