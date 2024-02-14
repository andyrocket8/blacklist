# Adapters for Redis like ISetDbEntity wrappers (Transform Any -> str for key and value - customizable)

from ipaddress import IPv4Address
from ipaddress import IPv4Network
from uuid import UUID

from src.models.ip_address_transformation import IPv4AddressStrTransformer
from src.models.ip_network_transformation import IPv4NetworkStrTransformer
from src.models.uuid_transformation import UUIDStrTransformer

from .base_set_db_entity import ISetDbEntity
from .base_set_db_entity_adapter import BaseSetDbEntityStrAdapter


class SetDbEntityStrAdapterUUID(BaseSetDbEntityStrAdapter[UUID, UUID], ISetDbEntity[UUID, UUID]):
    """Entity for sets with UUID as keys and UUID as values"""

    key_transformer = UUIDStrTransformer
    value_transformer = UUIDStrTransformer


class SetDbEntityStrAdapterIpAddress(BaseSetDbEntityStrAdapter[UUID, IPv4Address]):
    """Entity for sets with UUID as keys and IPv4Address as values"""

    key_transformer = UUIDStrTransformer
    value_transformer = IPv4AddressStrTransformer


class SetDbEntityStrAdapterIpNetwork(BaseSetDbEntityStrAdapter[UUID, IPv4Network]):
    """Entity for sets with UUID as keys and IPv4Network as values"""

    key_transformer = UUIDStrTransformer
    value_transformer = IPv4NetworkStrTransformer
