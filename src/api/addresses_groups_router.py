# Injectable router for addresses groups management
from src.api.handler_classes.addresses_group import AddressesGroup

allowed_addresses_api_router = AddressesGroup(group_category='allowed addresses').router()
banned_addresses_api_router = AddressesGroup(group_category='banned addresses').router()
