import logging
from datetime import datetime as dt_datetime
from typing import Any

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpNetwork
from src.db.storages.redis_db import RedisAsyncio
from src.schemas.addresses_schemas import IpV4AddressList
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.service.addresses_db_service import BlackListAddressesSetDBService
from src.service.networks_db_service import AllowedNetworksSetDBService
from src.service.process_banned_ips import without_allowed_ips


async def get_banned_addresses(redis_client_obj: RedisAsyncio, query_params: dict[str, Any]) -> IpV4AddressList:
    # TODO transform fetching logic to generator
    start_moment = dt_datetime.now()
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
        duration = dt_datetime.now() - start_moment
        logging.debug(
            'Finished blacklist query execution, elapsed %s milliseconds',
            duration.seconds + duration.microseconds / 1000,
        )
