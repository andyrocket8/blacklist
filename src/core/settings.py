import zoneinfo
from uuid import UUID

MSK_TZ = zoneinfo.ZoneInfo('Europe/Moscow')
CUR_TZ = MSK_TZ  # alias for current timezone. You are free to redeclare it in further implementations

POETRY_CONFIG_FIlE = 'pyproject.toml'

# Redis constants
BANNED_ADDRESSES_GROUPS_HASH_ID = UUID('1b282c3b-e2bd-45b8-847e-38d61a84a2a0')
ALLOWED_ADDRESSES_GROUPS_HASH_ID = UUID('49bb8147-9be4-4b35-9b1d-bcbe72ea5c27')

# Addresses Set Identifiers (Default Group)
BANNED_ADDRESSES_SET_ID = UUID('2c45911a-3d93-4dae-bd29-362b9880008f')
ALLOWED_ADDRESSES_SET_ID = UUID('7ee4e862-6932-41cf-8ef1-09bd80b04a69')
# Network Set Identifier
ALLOWED_NETWORKS_SET_ID = UUID('f35f7ce4-da01-4d82-8e43-5059aa30bfa8')

# Usage Set Identifiers
ACTIVE_USAGE_INFO = UUID('9cb46e89-8e7b-43e8-82a3-e7f3248c13a5')
HISTORY_USAGE_INFO = UUID('67f01230-365b-420f-9a09-8c01faf8193f')

# Auth Set Identifiers
# place in this set authorization token for agent methods (POST & DELETE methods)
AGENT_TOKENS_SET_ID = UUID('6f337b57-5135-427b-a52f-03390fdb8064')
# place in this set authorization token for administrator methods (All methods)
ADMIN_TOKENS_SET_ID = UUID('db3b6ec2-1c57-47e7-9ede-d7b51c4a374c')

# Temporarily sets expire period (in seconds)
SET_EXPIRE_SECONDS = 600

# Sets Constants
BATCH_SIZE = 1000
REDIS_FETCH_SIZE = 2000
BACKGROUND_ADD_RECORDS = 50
BACKGROUND_DELETE_RECORDS = 50
# Size of addresses storages implemented as lists (otherwise frozen set is used)
MAX_STORAGE_LIST_SIZE = 10
ALLOWED_NETWORKS_CACHE_SIZE = 1000

# History param detection mask
HISTORY_TIMEDELTA_MASK = r'^([0-9]+)([smhd]{1})$'


# Redis container name with tag
REDIS_DOCKER_IMAGE_NAME = 'redis:7.2.3-alpine3.18'

# Addresses constants
ALLOWED_ADDRESSES_CATEGORY_NAME = 'allowed addresses'
BANNED_ADDRESSES_CATEGORY_NAME = 'banned addresses'

# Default group consts
DEFAULT_GROUP_NAME = 'default'
DEFAULT_GROUP_DESCRIPTION = 'Default group'
ALLOWED_ADDRESSES_GROUP_NAME = ALLOWED_ADDRESSES_CATEGORY_NAME
BANNED_ADDRESSES_GROUP_NAME = BANNED_ADDRESSES_CATEGORY_NAME


# Usage options
HISTORY_PURGE_ON_LAST_DELETE_OPERATION = False  # Whether delete record in usage history on last delete operation
