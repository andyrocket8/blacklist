import logging
from asyncio import sleep as a_sleep
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import AsyncGenerator
from uuid import UUID

from fastapi import status

from src.core.settings import ALLOWED_NETWORKS_CACHE_SIZE
from src.utils.address_list_utils import AddressListServiceError
from src.utils.address_list_utils import retrieve_sets_from_params

from .abstract_set_db_entity_service import AbstractSetDBEntityService
from .networks_db_service import AllowedNetworksSetDBEntityService
from .service_db_factories import ServiceAdapters


class BlackListServiceError(AddressListServiceError):
    pass


class BlacklistService:
    def __init__(self, service_adapter_obj: ServiceAdapters):
        self.__service_adapter_obj: ServiceAdapters = service_adapter_obj

    async def retrieve_sets_from_params(self, groups_category_name: str, groups_in_param_query: str) -> list[UUID]:
        try:
            return await retrieve_sets_from_params(
                self.__service_adapter_obj.hash_db_service, groups_category_name, groups_in_param_query
            )
        except ValueError as e:
            # catch data validation errors here
            raise BlackListServiceError(
                str(e),
                status=status.HTTP_400_BAD_REQUEST,
            ) from None

    async def retrieve_exclude_data(self, allowed_set_id: UUID) -> tuple[set[IPv4Address], set[IPv4Network]]:
        # fill data with allowed addresses
        allowed_addresses_service_obj = AbstractSetDBEntityService[IPv4Address](
            self.__service_adapter_obj.address_set_db_entity, allowed_set_id
        )
        allowed_addresses_set: set[IPv4Address] = set()
        async for allowed_address in allowed_addresses_service_obj.fetch_records():
            allowed_addresses_set.add(allowed_address)
        # fill data with allowed networks
        allowed_networks_service_obj = AllowedNetworksSetDBEntityService(
            self.__service_adapter_obj.network_set_db_entity
        )
        allowed_networks_set: set[IPv4Network] = set()
        async for allowed_network in allowed_networks_service_obj.fetch_records():
            allowed_networks_set.add(allowed_network)

        return allowed_addresses_set, allowed_networks_set

    @staticmethod
    async def optimize_allowed_networks(
        allowed_networks: set[IPv4Network], allowed_addresses: set[IPv4Address]
    ) -> list[IPv4Network]:
        checked_allowed_networks: list[IPv4Network] = list()
        for allowed_network in allowed_networks:
            addresses_counter = 0
            for allowed_address in allowed_network.hosts():
                allowed_addresses.add(allowed_address)
                addresses_counter += 1
                if addresses_counter == ALLOWED_NETWORKS_CACHE_SIZE:
                    break
            if addresses_counter == ALLOWED_NETWORKS_CACHE_SIZE:
                # we have more address elements in allowed network, so we need to perform checks
                checked_allowed_networks.append(allowed_network)
            await a_sleep(0)
        return checked_allowed_networks

    async def get_banned_addresses(
        self,
        banned_set_id: UUID,
        allowed_addresses: set[IPv4Address],
        allowed_networks: set[IPv4Network],
        stop_records_count: int,
    ) -> AsyncGenerator[str, None]:
        allowed_addresses_local = allowed_addresses.copy()

        service_obj = AbstractSetDBEntityService(self.__service_adapter_obj.address_set_db_entity, banned_set_id)
        counter = 0
        # some optimization for networks,
        checked_allowed_networks: list[IPv4Network] = await self.optimize_allowed_networks(
            allowed_networks, allowed_addresses_local
        )
        logging.debug('Allowed networks size %d', len(checked_allowed_networks))
        async for address_record in service_obj.fetch_records():
            if address_record not in allowed_addresses_local:
                address_is_in_allowed_network = False
                for allowed_network in checked_allowed_networks:
                    if address_record in allowed_network:
                        address_is_in_allowed_network = True
                        logging.debug('Found banned %s in allowed network %s', address_record, allowed_network)
                if not address_is_in_allowed_network:
                    yield str(address_record) + '\n'
                    counter += 1
                    if counter >= stop_records_count > 0:
                        break
