"""Schemas for addresses (blacklisted or allowed)"""
from ipaddress import IPv4Address
from json import JSONEncoder

from .base_input_schema import BaseInputSchema

IpV4AddressList = list[IPv4Address]


class IpAddressEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)

        return JSONEncoder.default(self, o)


class AgentAddressesInfo(BaseInputSchema):
    """Information about addresses from agent"""

    addresses: IpV4AddressList
