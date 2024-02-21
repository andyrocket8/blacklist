# Methods for testing hash db entities classes
import random
from ipaddress import IPv4Address
from ipaddress import IPv4Network

from src.db.base_hash_db_entity import IHashDbEntity

from .test_hash_db_classes import AddressInfo
from .test_hash_db_classes import HostInfo
from .test_hash_db_classes import NetworkInfo


async def check_hash_contents(
    hash_db_entity_obj: IHashDbEntity[IPv4Network, IPv4Address, HostInfo], test_hash_data: NetworkInfo
):
    for record in test_hash_data.hosts:
        assert await hash_db_entity_obj.contains(
            test_hash_data.network, record.address
        ), 'Expect presence of record in test hash data'
        assert (
            await hash_db_entity_obj.read_value(test_hash_data.network, record.address) == record.host_info
        ), 'Mismatch in data stored in hash storage'


async def run_test_hash_db_entity(
    hash_db_entity_obj: IHashDbEntity[IPv4Network, IPv4Address, HostInfo], test_data: list[NetworkInfo]
):
    """Test of hash db entity (or adapter) with test sets"""
    # add data to hash storage
    for network_data in test_data:
        added_records = await hash_db_entity_obj.write_values(
            network_data.network,
            map(
                lambda x: (
                    x.address,
                    x.host_info,
                ),
                network_data.hosts,
            ),
        )
        # check the number of reported records
        assert added_records == len(network_data.hosts), 'Unexpected count of added records to hash storage'
        # check count of records in hash
        assert await hash_db_entity_obj.count(network_data.network) == len(
            network_data.hosts
        ), 'Count on storage is different than in test data'
        # check existence of all records
        await check_hash_contents(hash_db_entity_obj, network_data)
        # testing mass read operation
        async for address_info_obj in hash_db_entity_obj.fetch_records(network_data.network):
            address, host_info = address_info_obj
            assert (
                AddressInfo(address, host_info) in network_data.hosts
            ), 'Expect existence of fetched record in test data'
    # extra tests with partial data add
    # choose random set
    processed_hash_data: NetworkInfo = test_data[random.randint(0, len(test_data) - 1)]
    # delete some data from set (first and last record)
    deleted_records: int = await hash_db_entity_obj.delete_values(
        processed_hash_data.network,
        (processed_hash_data.hosts[0].address, processed_hash_data.hosts[len(processed_hash_data.hosts) - 1].address),
    )
    assert deleted_records == 2, 'Expected 2 deleted records'
    deleted_records = await hash_db_entity_obj.delete_values(
        processed_hash_data.network,
        (processed_hash_data.hosts[0].address, processed_hash_data.hosts[1].address),
    )
    assert deleted_records == 1, 'Expected 1 deleted records now'
    assert (
        await hash_db_entity_obj.count(processed_hash_data.network) == len(processed_hash_data.hosts) - 3
    ), 'Expected 3 records affect len of tested hash'
    # check None returned values on deleted records
    assert (
        await hash_db_entity_obj.read_value(processed_hash_data.network, processed_hash_data.hosts[0].address) is None
    ), 'Expected None value on read of deleted record'
    added_records = await hash_db_entity_obj.write_values(
        processed_hash_data.network,
        map(
            lambda x: (
                x.address,
                x.host_info,
            ),
            processed_hash_data.hosts,
        ),
    )
    assert added_records == 3, 'Expected 3 records be added to existing hash'
    # checking contents
    await check_hash_contents(hash_db_entity_obj, processed_hash_data)
