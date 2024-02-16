# Test for IP filters
from ipaddress import IPv4Address
from ipaddress import IPv4Network

import pytest

from src.service.process_banned_ips import without_allowed_ips


@pytest.fixture()
def allowed_networks() -> list[IPv4Network]:
    return [IPv4Network('172.0.0.0/8'), IPv4Network('192.168.1.0/24')]


BANNED_NETWORK = IPv4Network('10.100.0.0/16')


@pytest.fixture()
def banned_ips(allowed_networks: list[IPv4Network]) -> list[IPv4Address]:
    result = [x for x in BANNED_NETWORK]
    result.extend([x for x in allowed_networks[1]])
    return result


@pytest.fixture()
def allowed_ips() -> list[IPv4Address]:
    return [IPv4Address('10.100.0.1'), IPv4Address('10.100.0.24')]


@pytest.mark.asyncio
async def test_without_allowed_ips(
    banned_ips: list[IPv4Address], allowed_ips: list[IPv4Address], allowed_networks: list[IPv4Network]
):
    assert len(banned_ips) == 65536 + 256, 'Wrong banned ips length'
    filtered_ips = [x async for x in without_allowed_ips(banned_ips, allowed_ips, allowed_networks)]
    assert IPv4Address('10.100.0.1') not in filtered_ips, '10.100.0.1 should not be in result'
    assert IPv4Address('10.100.0.2') in filtered_ips, '10.100.0.2 should be in result'
    assert IPv4Address('192.168.1.1') not in filtered_ips, '192.168.1.1 should not be in result'
    assert IPv4Address('192.168.1.1') in banned_ips, '192.168.1.1 should be in banned IPs'
    assert len(filtered_ips) == len(banned_ips) - 256 - 2, 'Filtered IPs should consists of banned IPs minus 2 IPs'
