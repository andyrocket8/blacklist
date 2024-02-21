"""DB Service for usage history processing"""

from src.core.settings import ACTIVE_USAGE_INFO
from src.schemas.usage_schemas import UsageClassesEncoder
from src.schemas.usage_schemas import UsageRecord
from src.service.abstract_hkey_db_service import AbstractHkeyDBService


class UsageDBService(AbstractHkeyDBService[UsageRecord, UsageClassesEncoder]):
    """Service for current banned addresses usage information"""

    service_type = UsageRecord
    set_id = ACTIVE_USAGE_INFO
    json_encoder = UsageClassesEncoder
