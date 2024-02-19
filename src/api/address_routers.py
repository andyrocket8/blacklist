# Address routers (With AddressHandler)
from .handler_classes.addresses_handler import AddressHandler

banned_addresses_router = AddressHandler(
    address_category='banned', address_category_description='blacklist addresses'
).router()
