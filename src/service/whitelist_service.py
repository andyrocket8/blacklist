from ipaddress import IPv4Address
from typing import AsyncGenerator
from uuid import UUID

from fastapi import status

from src.utils.address_list_utils import AddressListServiceError
from src.utils.address_list_utils import retrieve_sets_from_params

from .abstract_set_db_entity_service import AbstractSetDBEntityService
from .networks_db_service import AllowedNetworksSetDBEntityService
from .service_db_factories import ServiceAdapters


class WhiteListServiceError(AddressListServiceError):
    pass


class WhitelistService:
    def __init__(self, service_adapter_obj: ServiceAdapters):
        self.__service_adapter_obj: ServiceAdapters = service_adapter_obj

    async def retrieve_sets_from_params(self, groups_category_name: str, groups_in_param_query: str) -> list[UUID]:
        try:
            return await retrieve_sets_from_params(
                self.__service_adapter_obj.hash_db_service, groups_category_name, groups_in_param_query
            )
        except ValueError as e:
            # catch data validation errors here
            raise WhiteListServiceError(
                str(e),
                status=status.HTTP_400_BAD_REQUEST,
            ) from None

    async def get_allowed_addresses(
        self,
        allowed_set_id: UUID,
        with_networks: bool,
        stop_records_count: int,
    ) -> AsyncGenerator[str, None]:
        records_count = 0
        if with_networks:
            # Fetch networks first
            allowed_networks_service_obj = AllowedNetworksSetDBEntityService(
                self.__service_adapter_obj.network_set_db_entity
            )
            async for allowed_network in allowed_networks_service_obj.fetch_records():
                yield str(allowed_network) + '\n'
            records_count += 1
            if records_count == stop_records_count:
                return
        # Now fetch addresses
        allowed_addresses_service_obj = AbstractSetDBEntityService[IPv4Address](
            self.__service_adapter_obj.address_set_db_entity, allowed_set_id
        )
        async for allowed_address in allowed_addresses_service_obj.fetch_records():
            yield str(allowed_address) + '\n'
            records_count += 1
            if records_count == stop_records_count:
                return
