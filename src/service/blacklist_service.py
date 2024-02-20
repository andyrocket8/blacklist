import logging
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import AsyncGenerator
from uuid import UUID

from fastapi import status

from src.schemas.set_group_schemas import GroupSet
from src.service.service_db_factories import groups_db_service_factory
from src.utils.misc_utils import split_str_list

from .abstract_set_db_entity_service import AbstractSetDBEntityService
from .networks_db_service import AllowedNetworksSetDBEntityService
from .service_db_factories import ServiceAdapters


class BlackListServiceError(Exception):
    def __init__(self, *args, **kwargs):
        self.status: int = kwargs.get('status', 500)


class BlacklistService:
    def __init__(self, service_adapter_obj: ServiceAdapters):
        self.__service_adapter_obj: ServiceAdapters = service_adapter_obj

    async def retrieve_sets_from_params(self, groups_category_name: str, groups_in_param_query: str) -> list[UUID]:
        """Parse group info and return information of retrieved sets"""
        groups_in_param = split_str_list(groups_in_param_query)
        groups_service_obj = groups_db_service_factory(groups_category_name, self.__service_adapter_obj.hash_db_service)
        parsed_groups: list[GroupSet] = await groups_service_obj.list_groups()
        retrieved_sets: list[UUID] = []
        if groups_in_param:
            for param_group_name in groups_in_param:
                # suppose we have small count of groups ... iterating on groups list
                for group_in_storage in parsed_groups:
                    if group_in_storage.group_name == param_group_name:
                        retrieved_sets.append(group_in_storage.group_set_id)
                        break
                else:
                    raise BlackListServiceError(
                        f'Group with name {param_group_name} is not found in {groups_category_name} groups',
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        else:
            # on empty groups list fill all groups
            for group_in_storage in parsed_groups:
                retrieved_sets.append(group_in_storage.group_set_id)
        return retrieved_sets

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

    async def get_banned_addresses(
        self,
        banned_set_id: UUID,
        allowed_addresses: set[IPv4Address],
        allowed_networks: set[IPv4Network],
        stop_records_count: int,
    ) -> AsyncGenerator[str, None]:
        service_obj = AbstractSetDBEntityService(self.__service_adapter_obj.address_set_db_entity, banned_set_id)
        counter = 0
        async for address_record in service_obj.fetch_records():
            if address_record not in allowed_addresses:
                address_is_in_allowed_network = False
                for allowed_network in allowed_networks:
                    if address_record in allowed_network:
                        address_is_in_allowed_network = True
                        logging.warning('Found banned %s in allowed network %s', address_record, allowed_network)
                if not address_is_in_allowed_network:
                    yield str(address_record) + '\n'
                    counter += 1
                    if counter >= stop_records_count > 0:
                        break

    async def remove_temp_sets(self, erased_sets: list[UUID]):
        for eliminated_set in erased_sets:
            await self.__service_adapter_obj.set_db.del_set(eliminated_set)
            logging.debug('Deleting temporarily set in background, set ID: %s', eliminated_set)
