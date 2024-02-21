# Whitelist router
import logging
from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from src.api.di.db_di_routines import download_handle_adapters
from src.core.settings import ALLOWED_ADDRESSES_GROUP_NAME
from src.core.settings import SET_EXPIRE_SECONDS
from src.models.query_params_models import DownloadWhitelistQueryParams
from src.service.service_db_factories import ServiceAdapters
from src.service.whitelist_service import WhitelistService
from src.service.whitelist_service import WhiteListServiceError
from src.tasks.set_management_bg_tasks import delete_temp_sets_bg

api_router = APIRouter()


@api_router.get('', summary='Get whitelisted addresses as a file')
async def allowed_addresses_as_file(
    service_adapter_obj: Annotated[ServiceAdapters, Depends(download_handle_adapters)],
    query_params: Annotated[DownloadWhitelistQueryParams, Depends()],
    background_tasks: BackgroundTasks,
):
    try:
        teardown_sets: list[UUID] = list()
        whitelist_service_obj = WhitelistService(service_adapter_obj)
        headers = dict()
        allowed_group_sets = await whitelist_service_obj.retrieve_sets_from_params(
            ALLOWED_ADDRESSES_GROUP_NAME, query_params.allowed_groups
        )
        assert len(allowed_group_sets) > 0, 'Sets list for allowed addresses should have one or more values'
        if len(allowed_group_sets) > 1:
            # create temporarily set
            allowed_set_id = await service_adapter_obj.union_set_db.union_set(allowed_group_sets)
            logging.debug('Created temporarily set for allowed addresses in background, set ID: %s', allowed_set_id)
            await service_adapter_obj.set_db.set_ttl(allowed_set_id, SET_EXPIRE_SECONDS)
            teardown_sets.append(allowed_set_id)
        else:
            allowed_set_id = allowed_group_sets[0]

        filename = query_params.filename
        if filename:
            content_disposition_type = 'attachment'
            content_disposition_filename = filename
            headers['Content-Disposition'] = "{}; filename*=utf-8''{}".format(
                content_disposition_type, quote(content_disposition_filename)
            )

        records_count: int = 0 if query_params.all_records else query_params.records_count

        # add teardown task for clearing temporarily sets
        background_tasks.add_task(delete_temp_sets_bg, teardown_sets)
        # Need to fetch all data here
        result = list()
        accumulated = ''
        async for address in whitelist_service_obj.get_allowed_addresses(
            allowed_set_id, query_params.with_networks, records_count
        ):
            accumulated += address
            if len(accumulated) > 10000:
                result.append(accumulated)
                accumulated = ''
        result.append(accumulated)
        logging.debug('Finish gathering result, records count: %d', len(result))
        return StreamingResponse(
            result,
            media_type='text/plain',
            headers=headers,
        )

    except WhiteListServiceError as e:
        logging.error(str(e))
        raise HTTPException(status_code=e.status, detail=str(e)) from None
