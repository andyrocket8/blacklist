""" Schemas for networks"""

from ipaddress import IPv4Network
from typing import Iterable

from .base_input_schema import BaseInputSchema

IPv4NetworkList = list[IPv4Network]
IPv4NetworkIterable = Iterable[IPv4Network]


class AgentNetworkInfo(BaseInputSchema):
    """Information about networks from agent"""

    networks: IPv4NetworkList
