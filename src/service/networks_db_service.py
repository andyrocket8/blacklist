from ipaddress import IPv4Network

from src.core.settings import ALLOWED_NETWORKS_SET_ID

from .abstract_set_db_entity_service import AbstractSetDBEntityService


class AllowedNetworksSetDBEntityService(AbstractSetDBEntityService[IPv4Network]):
    class_set_id = ALLOWED_NETWORKS_SET_ID
