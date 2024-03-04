from datetime import datetime as dt_datetime
from ipaddress import IPv4Address

from src.core.settings import MSK_TZ
from src.core.settings import UTC_TZ
from src.models.usage_transformation import SURDictTransformation
from src.schemas.usage_schemas import ActionType
from src.schemas.usage_schemas import StreamUsageRecord

TEST_USAGE_FIXTURE: list[tuple[StreamUsageRecord, dict[str, str]]] = [
    (
        StreamUsageRecord(
            action_type=ActionType.add_action,
            action_time=dt_datetime(2024, 2, 1, 12, 23, 4, tzinfo=MSK_TZ),
            addresses={IPv4Address('10.100.0.1'), IPv4Address('10.100.0.2'), IPv4Address('10.100.0.3')},
            address_category=None,
            address_group=None,
        ),
        {
            'action_type': 'add',
            'action_time': '2024-02-01T12:23:04.000000+0300',
            'addresses': '10.100.0.1:10.100.0.2:10.100.0.3',
        },
    ),
    (
        StreamUsageRecord(
            action_type=ActionType.remove_action,
            action_time=dt_datetime(2024, 2, 1, 12, 23, 4),
            addresses={
                IPv4Address('10.100.0.1'),
                IPv4Address('10.100.0.4'),
                IPv4Address('10.100.0.2'),
                IPv4Address('10.100.0.3'),
            },
            address_category='',
            address_group=None,
        ),
        {
            'action_type': 'remove',
            'action_time': '2024-02-01T12:23:04.000000',
            'addresses': '10.100.0.1:10.100.0.2:10.100.0.3:10.100.0.4',
            'address_category': '',
        },
    ),
    (
        StreamUsageRecord(
            action_type=ActionType.remove_action,
            action_time=dt_datetime(2022, 1, 3, 23, 1, 5, tzinfo=UTC_TZ),
            addresses={'10.100.0.1'},
            address_category='category_01',
            address_group='group_02',
        ),
        {
            'action_type': 'remove',
            'action_time': '2022-01-03T23:01:05.000000+0000',
            'addresses': '10.100.0.1',
            'address_category': 'category_01',
            'address_group': 'group_02',
        },
    ),
]


class StreamUsageRecordDict(dict):
    def __eq__(self, other) -> bool:

        return (
            self.get('action_type') == other.get('action_type')
            and self.get('action_time') == other.get('action_time')
            and self.get('action_category', None) == other.get('action_category', None)
            and self.get('action_category', None) == other.get('action_category', None)
            and sorted(self['addresses'].split(':')) == sorted(other['addresses'].split(':'))
        )


def test_usage_transformation():
    for sur_obj, dict_obj in TEST_USAGE_FIXTURE:
        assert SURDictTransformation.transform_to_storage(sur_obj) == StreamUsageRecordDict(
            dict_obj
        ), 'Expected nice transformation to dict'
        assert (
            SURDictTransformation.transform_from_storage(dict_obj) == sur_obj
        ), 'Expected nice transformation from dict'
