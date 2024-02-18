# Injectable router for addresses groups management
from src.api.handler_classes.addresses_group_handler import AddressesGroupHandler

allowed_addresses_api_router = AddressesGroupHandler(group_category='allowed addresses').router()
banned_addresses_api_router = AddressesGroupHandler(group_category='banned addresses').router()
