from ipaddress import IPv4Network

from src.core.settings import ALLOWED_NETWORKS_SET_ID

from .abstract_db_service import AbstractDBService


class AllowedNetworksDBService(AbstractDBService[IPv4Network]):
    service_type = IPv4Network
    set_id = ALLOWED_NETWORKS_SET_ID
