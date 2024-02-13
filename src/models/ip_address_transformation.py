from ipaddress import IPv4Address

from .transformation import Transformation


class IPv4AddressStrTransformer(Transformation[IPv4Address, str]):
    """Transformation from UUID to internal str for Redis"""

    @classmethod
    def transform_to_storage(cls, value: IPv4Address) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> IPv4Address:
        return IPv4Address(value)
