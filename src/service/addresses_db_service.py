from ipaddress import IPv4Address

from src.core.settings import ALLOWED_ADDRESSES_SET_ID
from src.core.settings import BANNED_ADDRESSES_SET_ID

from .abstract_set_db_entity_service import AbstractSetDBEntityService
from .abstract_set_db_service import AbstractSetDBService


class BlackListAddressesSetDBService(AbstractSetDBService[IPv4Address]):
    """Serve set management routines with black list addresses in Redis database"""

    class_set_id = BANNED_ADDRESSES_SET_ID


class BlackListAddressesSetDBEntityService(AbstractSetDBEntityService[IPv4Address]):
    """Serve operations with black list addresses in Redis database"""

    class_set_id = BANNED_ADDRESSES_SET_ID


class AllowedAddressesSetDBService(AbstractSetDBService[IPv4Address]):
    """Serve set management routines with allowed addresses in Redis database"""

    class_set_id = ALLOWED_ADDRESSES_SET_ID


class AllowedAddressesSetDBEntityService(AbstractSetDBEntityService[IPv4Address]):
    """Serve operations with allowed addresses in Redis database"""

    class_set_id = ALLOWED_ADDRESSES_SET_ID


class AnyAddressesSetDBEntityService(AbstractSetDBEntityService[IPv4Address]):
    """Define set ID in the __init__ function!"""

    pass
