import json
from base64 import b64decode
from base64 import b64encode
from dataclasses import dataclass
from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import Type

from src.db.adapters.base_hash_db_entity_adapter import IHashDbEntityAdapter
from src.models.transformation import Transformation


@dataclass
class HostInfo:
    host_name: str
    host_description: str
    signature: bytes


@dataclass
class AddressInfo:
    address: IPv4Address
    host_info: HostInfo


@dataclass
class NetworkInfo:
    network: IPv4Network
    hosts: list[AddressInfo]


class TransformIPv4Network(Transformation[IPv4Network, str]):
    @classmethod
    def transform_to_storage(cls, value: IPv4Network) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> IPv4Network:
        return IPv4Network(value)


class TransformIPv4Address(Transformation[IPv4Address, str]):
    @classmethod
    def transform_to_storage(cls, value: IPv4Address) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> IPv4Address:
        return IPv4Address(value)


class TransformHostInfo(Transformation[HostInfo, str]):
    @classmethod
    def transform_to_storage(cls, value: HostInfo) -> str:
        # first of all transform to json
        dict_data = {
            'host_name': value.host_name,
            'host_description': value.host_description,
            'signature_b64': b64encode(value.signature).decode(),
        }
        return b64encode(json.dumps(dict_data).encode()).decode()

    @classmethod
    def transform_from_storage(cls, value: str) -> HostInfo:
        # back operation
        dict_data = json.loads(b64decode(value.encode()).decode())
        signature_b64 = dict_data.pop('signature_b64')
        dict_data['signature'] = b64decode(signature_b64.encode())
        return HostInfo(**dict_data)


class HashDbEntityNetworkInfoAdapter(IHashDbEntityAdapter[IPv4Network, IPv4Address, HostInfo, str, str, str]):
    # Adapter for transformation into 'all attributes str' storage
    hash_transformer: Type[Transformation[IPv4Network, str]] = TransformIPv4Network
    key_transformer: Type[Transformation[IPv4Address, str]] = TransformIPv4Address
    value_transformer: Type[Transformation[HostInfo, str]] = TransformHostInfo
