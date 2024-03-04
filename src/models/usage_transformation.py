from ipaddress import IPv4Address
from typing import Optional

from src.schemas.usage_schemas import ActionType
from src.schemas.usage_schemas import StreamUsageRecord
from src.utils.time_utils import decode_datetime
from src.utils.time_utils import encode_datetime

from .transformation import Transformation


class SURDictTransformation(Transformation[StreamUsageRecord, dict[str, str]]):
    """Interface for transformation data within storage"""

    @classmethod
    def transform_to_storage(cls, value: StreamUsageRecord) -> dict[str, str]:
        addresses_str = ':'.join(str(x) for x in value.addresses)
        return (
            {
                'action_type': value.action_type.value,
                'action_time': encode_datetime(value.action_time),
                'addresses': addresses_str,
            }
            | ({'address_category': value.address_category} if value.address_category is not None else {})
            | ({'address_group': value.address_group} if value.address_group is not None else {})
        )

    @classmethod
    def transform_from_storage(cls, value: dict[str, str]) -> StreamUsageRecord:
        address_category: Optional[str] = value.get('address_category', None)
        address_group: Optional[str] = value.get('address_group', None)
        return StreamUsageRecord(
            action_type=ActionType(value['action_type']),
            action_time=decode_datetime(value['action_time']),
            addresses=set(map(lambda x: IPv4Address(x), value['addresses'].split(':'))),
            address_category=address_category,
            address_group=address_group,
        )
