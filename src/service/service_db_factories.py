from dataclasses import dataclass
from uuid import UUID

from src.core.settings import ALLOWED_ADDRESSES_CATEGORY_NAME
from src.core.settings import ALLOWED_ADDRESSES_GROUP_NAME
from src.core.settings import ALLOWED_ADDRESSES_GROUPS_HASH_ID
from src.core.settings import ALLOWED_ADDRESSES_SET_ID
from src.core.settings import BANNED_ADDRESSES_CATEGORY_NAME
from src.core.settings import BANNED_ADDRESSES_GROUP_NAME
from src.core.settings import BANNED_ADDRESSES_GROUPS_HASH_ID
from src.core.settings import BANNED_ADDRESSES_SET_ID
from src.db.base_hash_db_entity import IHashDbEntity
from src.db.base_set_db_entity import ISetDbEntity
from src.service.abstract_set_db_service import AbstractSetDBService
from src.service.addresses_db_service import AllowedAddressesSetDBService
from src.service.addresses_db_service import AnyAddressesSetDBService
from src.service.addresses_db_service import BlackListAddressesSetDBService
from src.service.groups_db_service import GroupsDbService


# Groups DB services factory utilities
def banned_groups_db_service(db_service_adapter: IHashDbEntity) -> GroupsDbService:
    """Return service of certain type"""
    return GroupsDbService(
        db_service_adapter,
        BANNED_ADDRESSES_GROUPS_HASH_ID,
        BANNED_ADDRESSES_SET_ID,
    )


def allowed_groups_db_service(db_service_adapter: IHashDbEntity) -> GroupsDbService:
    """Return service of certain type"""
    return GroupsDbService(
        db_service_adapter,
        ALLOWED_ADDRESSES_GROUPS_HASH_ID,
        ALLOWED_ADDRESSES_SET_ID,
    )


def groups_db_service_factory(group_name: str, db_service_adapter: IHashDbEntity) -> GroupsDbService:
    if group_name == ALLOWED_ADDRESSES_GROUP_NAME:
        return allowed_groups_db_service(db_service_adapter)
    elif group_name == BANNED_ADDRESSES_GROUP_NAME:
        return banned_groups_db_service(db_service_adapter)
    else:
        raise ValueError('Incorrect value of group name passed to groups_db_service_factory')


def addresses_db_service_factory(address_category_name: str, db_service_adapter: ISetDbEntity) -> AbstractSetDBService:
    if address_category_name == ALLOWED_ADDRESSES_CATEGORY_NAME:
        return AllowedAddressesSetDBService(db_service_adapter)
    elif address_category_name == BANNED_ADDRESSES_CATEGORY_NAME:
        return BlackListAddressesSetDBService(db_service_adapter)
    else:
        raise ValueError('Incorrect value of address category name passed to addresses_db_service_factory')


def any_addresses_db_service_factory(set_id: UUID, db_service_adapter: ISetDbEntity) -> AbstractSetDBService:
    return AnyAddressesSetDBService(db_service_adapter, set_id=set_id)


@dataclass
class ServiceWithGroupDbAdapters:
    db_service_adapter: ISetDbEntity
    db_hash_service_adapter: IHashDbEntity


@dataclass
class ServiceWithGroups:
    addresses_db_service: AbstractSetDBService
    groups_db_service: GroupsDbService


def addresses_with_groups_db_service_factory(
    address_category_name: str, adapters: ServiceWithGroupDbAdapters
) -> ServiceWithGroups:
    groups_db_service: GroupsDbService = groups_db_service_factory(
        address_category_name, adapters.db_hash_service_adapter
    )
    if address_category_name == ALLOWED_ADDRESSES_CATEGORY_NAME:
        return ServiceWithGroups(
            addresses_db_service=AllowedAddressesSetDBService(adapters.db_service_adapter),
            groups_db_service=groups_db_service,
        )
    elif address_category_name == BANNED_ADDRESSES_CATEGORY_NAME:
        return ServiceWithGroups(
            addresses_db_service=BlackListAddressesSetDBService(adapters.db_service_adapter),
            groups_db_service=groups_db_service,
        )
    else:
        raise ValueError('Incorrect value of address category name passed to addresses_db_service_factory')
