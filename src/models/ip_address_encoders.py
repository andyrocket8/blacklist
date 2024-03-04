# Encoders for IP address entities

from datetime import datetime as dt_datetime
from ipaddress import IPv4Address
from json import JSONEncoder


class IpAddressEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)
        if type(o) is dt_datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

        return JSONEncoder.default(self, o)


class AgentAddressesInfoEncoder(JSONEncoder):
    def default(self, o):
        if type(o) is IPv4Address:
            return str(o)
        if type(o) is dt_datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        if o.__class__.__name__ == 'AgentAddressesInfo':
            return o.model_dump(mode='json')

        return JSONEncoder.default(self, o)
