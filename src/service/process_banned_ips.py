import logging
from asyncio import sleep
from ipaddress import IPv4Address
from typing import AsyncGenerator
from typing import Union

from src.core.settings import MAX_STORAGE_LIST_SIZE
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.network_schemas import IPv4NetworkList


def adopt_address_storage(addresses: IpV4AddressList) -> Union[frozenset[IPv4Address], IpV4AddressList]:
    if len(addresses) > MAX_STORAGE_LIST_SIZE:
        return frozenset(addresses)
    return addresses


async def without_allowed_ips(
    banned_ips: IpV4AddressList, allowed_ips: IpV4AddressList, allowed_networks: IPv4NetworkList
) -> AsyncGenerator[IPv4Address, None]:
    """Filter banned IPs"""
    allowed_ips_adopted = adopt_address_storage(allowed_ips)
    for address in banned_ips:
        if address not in allowed_ips_adopted:
            address_is_in_allowed_network = False
            for allowed_network in allowed_networks:
                if address in allowed_network:
                    address_is_in_allowed_network = True
                    logging.warning('Found banned %s in allowed network %s', address, allowed_network)
            if not address_is_in_allowed_network:
                yield address
        await sleep(0)
