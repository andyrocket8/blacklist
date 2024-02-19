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
