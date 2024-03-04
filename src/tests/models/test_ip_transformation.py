from dataclasses import dataclass
from ipaddress import IPv4Address

from src.models.ip_address_transformation import IPv4AddressListStrTransformer
from src.models.ip_address_transformation import IPv4AddressSetStrTransformer


@dataclass
class ListDataForTest:
    source_data: list[IPv4Address]
    target: str


TEST_LIST_DATA: list[ListDataForTest] = [
    ListDataForTest(
        [IPv4Address('10.100.0.1'), IPv4Address('10.100.0.2'), IPv4Address('10.100.0.3')],
        '10.100.0.1:10.100.0.2:10.100.0.3',
    ),
    ListDataForTest([IPv4Address('10.100.0.1')], '10.100.0.1'),
    ListDataForTest([], ''),
]


def test_ip_addr_list_transformer():
    for test_record in TEST_LIST_DATA:
        assert IPv4AddressListStrTransformer.transform_to_storage(test_record.source_data) == test_record.target
        assert IPv4AddressListStrTransformer.transform_from_storage(test_record.target) == test_record.source_data


def test_ip_addr_set_transformer():
    for test_record in TEST_LIST_DATA:
        source_set = set(test_record.source_data)
        target = IPv4AddressSetStrTransformer.transform_to_storage(source_set)
        target_splitted = target.split(':')
        if len(test_record.source_data):
            assert len(target_splitted) == len(test_record.source_data)
            for value in target_splitted:
                assert IPv4Address(value) in source_set
        extracted_set = IPv4AddressSetStrTransformer.transform_from_storage(test_record.target)
        assert source_set == extracted_set
