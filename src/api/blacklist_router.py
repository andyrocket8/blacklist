# Blacklist router
import logging
from datetime import datetime as dt_datetime
from ipaddress import IPv4Address
from ipaddress import IPv4Network
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
from src.core.settings import BANNED_ADDRESSES_GROUP_NAME
from src.core.settings import SET_EXPIRE_SECONDS
from src.models.query_params_models import DownloadBlackListQueryParams
from src.service.blacklist_service import BlacklistService
from src.service.blacklist_service import BlackListServiceError
from src.service.service_db_factories import ServiceAdapters

api_router = APIRouter()

'''
   Algorithm detailed descriprion:
   Getting data from banned address groups. Filter with allowed addresses and networks

   Path:
   1) load banned addresses groups
   2) if query_params.banned_address_groups is passed in params:
      - parse specified in parameter groups, check them and make temporarily united set in storage
      - otherwise suppose we get all data from all banned sets
   2) if we get data from all banned sets
      - check the count of banned address groups. If it equals to 1 then no need to merge sets.
      - otherwise compose temporarily set from all banned groups.
   2) if query_params.filter_records is True then we must prepare filter data
     - if query_params.allowed_address_groups is set:
       - parse specified groups, check them and make temporarily united set in storage
       - otherwise we get data from all allowed sets
     - if we get all data from all allowed sets:
       - check the count of allowed address groups. If it equals to 1 then no need to merge sets.
       - otherwise compose temporarily set from all allowed groups.
     - prepare data for filtering:
       - read allowed addresses from allowed set (from one prepared set or only one)
       - transform it to set for faster search
       - read allowed networks from allowed networks set
       - transform it to set for faster search
   !!! set TTL to all temporarily sets
   3) prepare generator for fetching data from banned set and filtering it with allowed sets (addresses and networks)
      if we need filtering
   4) produce recordset for response
   5) teardown all temporarily sets after execution in background task. If background task is not started then storage
   remove it after timeout

   As DI to connect to storage we need
   1) Service to work with addresses (with ISetDbEntity interface)
   2) Service to work with SetDB (to set TTL for temporarily sets) (with ISetDb interface)
   3) Service to merge sets (with IUnionSetDb interface)
   4) Service for managing address groups (IHashDbS
'''


@api_router.get('', summary='Get blacklisted addresses as a file')
async def banned_addresses_as_file(
    service_adapter_obj: Annotated[ServiceAdapters, Depends(download_handle_adapters)],
    query_params: Annotated[DownloadBlackListQueryParams, Depends()],
    background_tasks: BackgroundTasks,
):
    logging.debug('Starting blacklist query execution')
    start_moment = dt_datetime.now()

    blacklist_service_obj = BlacklistService(service_adapter_obj)
    try:
        teardown_sets: list[UUID] = list()
        # get information on passed banned sets
        banned_group_sets = await blacklist_service_obj.retrieve_sets_from_params(
            BANNED_ADDRESSES_GROUP_NAME, query_params.banned_address_groups
        )
        assert len(banned_group_sets) > 0, 'Sets list for banned addresses should have one or more values'
        if len(banned_group_sets) > 1:
            # create temporarily set
            banned_set_id = await service_adapter_obj.union_set_db.union_set(banned_group_sets)
            logging.debug('Created temporarily set for banned addresses in background, set ID: %s', banned_set_id)
            await service_adapter_obj.set_db.set_ttl(banned_set_id, SET_EXPIRE_SECONDS)
            teardown_sets.append(banned_set_id)
        else:
            banned_set_id = banned_group_sets[0]
        # check filtering now
        allowed_addresses_set: set[IPv4Address]
        allowed_networks_set: set[IPv4Network]

        if query_params.filter_records:
            allowed_group_set_list: list[UUID] = await blacklist_service_obj.retrieve_sets_from_params(
                ALLOWED_ADDRESSES_GROUP_NAME, query_params.allowed_address_groups
            )
            # set allowed_set_id with only ID or None if we have empty
            assert len(allowed_group_set_list) > 0, 'Sets list for allowed addresses should have one or more values'
            if len(allowed_group_set_list) > 1:
                # create temporarily set
                allowed_set_id = await service_adapter_obj.union_set_db.union_set(allowed_group_set_list)
                logging.debug('Created temporarily set for allowed addresses in background, set ID: %s', allowed_set_id)
                await service_adapter_obj.set_db.set_ttl(allowed_set_id, SET_EXPIRE_SECONDS)
                teardown_sets.append(allowed_set_id)
            else:
                allowed_set_id = allowed_group_set_list[0]
            allowed_addresses_set, allowed_networks_set = await blacklist_service_obj.retrieve_exclude_data(
                allowed_set_id
            )
        else:
            allowed_addresses_set, allowed_networks_set = set(), set()

        filename = query_params.filename
        headers = dict()
        if filename:
            content_disposition_type = 'attachment'
            content_disposition_filename = filename
            headers['Content-Disposition'] = "{}; filename*=utf-8''{}".format(
                content_disposition_type, quote(content_disposition_filename)
            )
        records_count: int = 0 if query_params.all_records else query_params.records_count
        # add teardown task for clearing temporarily sets
        background_tasks.add_task(blacklist_service_obj.remove_temp_sets, teardown_sets)
        return StreamingResponse(
            blacklist_service_obj.get_banned_addresses(
                banned_set_id, allowed_addresses_set, allowed_networks_set, records_count
            ),
            media_type='text/plain',
            headers=headers,
        )
    except BlackListServiceError as e:
        logging.error(str(e))
        raise HTTPException(status_code=e.status, detail=str(e)) from None

    finally:
        duration = dt_datetime.now() - start_moment
        logging.debug(
            'Finished blacklist query execution, elapsed %s milliseconds',
            duration.seconds + duration.microseconds / 1000,
        )
