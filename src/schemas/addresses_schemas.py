"""Schemas for addresses (blacklisted or allowed)"""

import datetime
from ipaddress import IPv4Address
from json import JSONEncoder
from typing import Optional

from .base_input_schema import BaseInputSchema

IpV4AddressList = list[IPv4Address]


class IpAddressEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)
        if type(o) is datetime.datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

        return JSONEncoder.default(self, o)


class AgentAddressesInfoEncoder(JSONEncoder):
    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)
        if type(o) is datetime.datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        if o.__class__.__name__ == 'AgentAddressesInfo':
            return o.model_dump(mode='json')

        return JSONEncoder.default(self, o)


class AgentAddressesInfo(BaseInputSchema):
    """Information about addresses from agent"""

    addresses: IpV4AddressList

    def encode(self):
        return self.model_dump(mode='json')


class AgentAddressesInfoWithGroup(AgentAddressesInfo):
    """Adopted information with addresses group included. If not specified - it is treated as default"""

    address_group: Optional[str] = None
