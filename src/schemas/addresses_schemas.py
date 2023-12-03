"""Schemas for blacklisted addresses"""
from ipaddress import IPv4Address
from json import JSONEncoder

from pydantic import BaseModel


class IpAddressEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)

        return JSONEncoder.default(self, o)


class AgentAddressesInfo(BaseModel):
    """Information about addresses from agent"""

    source_agent: str
    addresses: list[IPv4Address]
