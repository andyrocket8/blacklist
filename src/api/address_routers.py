# Address routers (With AddressHandler)
from src.core.settings import ALLOWED_ADDRESSES_CATEGORY_NAME
from src.core.settings import BANNED_ADDRESSES_CATEGORY_NAME

from .handler_classes.addresses_handler import AddressHandler

banned_addresses_router = AddressHandler(
    address_category=BANNED_ADDRESSES_CATEGORY_NAME, address_category_description='blacklist addresses'
).router()

allowed_addresses_router = AddressHandler(
    address_category=ALLOWED_ADDRESSES_CATEGORY_NAME, address_category_description='whitelist addresses'
).router()
