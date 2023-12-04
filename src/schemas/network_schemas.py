""" Schemas for networks"""
from ipaddress import IPv4Network
from json import JSONEncoder

from .base_input_schema import BaseInputSchema


class IpNetworkEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is IPv4Network:
            return str(o)

        return JSONEncoder.default(self, o)


class AgentNetworkInfo(BaseInputSchema):
    """Information about networks from agent"""

    networks: list[IPv4Network]
