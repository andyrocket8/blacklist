"""Schemas for addresses (blacklisted or allowed)"""

from ipaddress import IPv4Address
from typing import Optional

from .base_input_schema import BaseInputSchema

IpV4AddressList = list[IPv4Address]


class AgentAddressesInfo(BaseInputSchema):
    """Information about addresses from agent"""

    addresses: IpV4AddressList

    def encode(self):
        return self.model_dump(mode='json')


class AgentAddressesInfoWithGroup(AgentAddressesInfo):
    """Adopted information with addresses group included. If not specified - it is treated as default"""

    address_group: Optional[str] = None
