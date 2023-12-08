from ipaddress import IPv4Address
from random import randint
from typing import Generator
from typing import Optional

from src.schemas.addresses_schemas import IpV4AddressList

MAX_IP_ADDRESS = pow(2, 32) - 1


def gen_random_ip(max_count: Optional[int] = None) -> Generator[IPv4Address, None, None]:
    """Generator for random IP creation"""
    step = 0
    while True:
        yield IPv4Address(randint(1, MAX_IP_ADDRESS))
        if max_count is not None:
            step += 1
            if step >= max_count:
                break


def random_ip_addresses(count: int) -> IpV4AddressList:
    """Generate random IP addresses"""
    return [x for x in gen_random_ip(count)]
