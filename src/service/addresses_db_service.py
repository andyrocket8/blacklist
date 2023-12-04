from ipaddress import IPv4Address

from src.core.settings import ALLOWED_ADDRESSES_SET_ID
from src.core.settings import BLACK_LIST_ADDRESSES_SET_ID

from .abstract_db_service import AbstractDBService


class BlackListAddressesDBService(AbstractDBService[IPv4Address]):
    """Serve operations with black list addresses in Redis database"""

    service_type = IPv4Address
    set_id = BLACK_LIST_ADDRESSES_SET_ID


class AllowedAddressesDBService(AbstractDBService[IPv4Address]):
    """Serve operations with allowed addresses in Redis database"""

    service_type = IPv4Address
    set_id = ALLOWED_ADDRESSES_SET_ID
