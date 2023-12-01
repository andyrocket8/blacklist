# Schemas for blacklisted addresses
from ipaddress import IPv4Address

from pydantic import BaseModel


class AgentAddressesInfo(BaseModel):
    """ Information about addresses from agent """
    source_agent: str
    addresses: list[IPv4Address]
