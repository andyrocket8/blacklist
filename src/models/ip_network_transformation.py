from ipaddress import IPv4Network

from .transformation import Transformation


class IPv4NetworkStrTransformer(Transformation[IPv4Network, str]):
    """Transformation from UUID to internal str for Redis"""

    @classmethod
    def transform_to_storage(cls, value: IPv4Network) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> IPv4Network:
        return IPv4Network(value)
