from ipaddress import IPv4Network

from src.core.settings import ALLOWED_NETWORKS_SET_ID

from .abstract_set_db_service import AbstractSetDBService


class AllowedNetworksSetDBService(AbstractSetDBService[IPv4Network]):
    service_type = IPv4Network
    set_id = ALLOWED_NETWORKS_SET_ID
