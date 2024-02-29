from ipaddress import IPv4Address

from .transformation import Transformation


class IPv4AddressStrTransformer(Transformation[IPv4Address, str]):
    """Transformation from IPv4Address to internal str for Redis"""

    @classmethod
    def transform_to_storage(cls, value: IPv4Address) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> IPv4Address:
        return IPv4Address(value)


class IPv4AddressListStrTransformer(Transformation[list[IPv4Address], str]):
    """Transformation from IPv4Address list to internal str for Redis
    Transform to similar string as in sample: 10.100.0.1:10.100.0.2:.... <-> list of IPv4Address
    """

    @classmethod
    def transform_to_storage(cls, values: list[IPv4Address]) -> str:
        return ':'.join(map(str, values))

    @classmethod
    def transform_from_storage(cls, values: str) -> list[IPv4Address]:
        return [x for x in map(IPv4Address, values.split(':'))] if values else []


class IPv4AddressSetStrTransformer(Transformation[set[IPv4Address], str]):
    """Transformation from IPv4Address set to internal str for Redis
    Transform to similar string as in sample: 10.100.0.1:10.100.0.2:.... <-> set of IPv4Address
    """

    @classmethod
    def transform_to_storage(cls, values: set[IPv4Address]) -> str:
        return ':'.join(map(str, values))

    @classmethod
    def transform_from_storage(cls, values: str) -> set[IPv4Address]:
        return set(map(IPv4Address, values.split(':'))) if values else set()
