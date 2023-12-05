"""DB Service for usage history processing"""
from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import HISTORY_USAGE_INFO
from src.schemas.usage_schemas import HistoryRecord
from src.schemas.usage_schemas import UsageRecord

from .abstract_hkey_db_service import AbstractHkeyDBService


class UsageDBService(AbstractHkeyDBService[UsageRecord]):
    """Service for current banned addresses usage information"""

    service_type = UsageRecord
    set_id = ACTIVE_USAGE_INFO


class HistoryDBService(AbstractHkeyDBService[HistoryRecord]):
    """Service for current banned addresses usage information"""

    service_type = HistoryRecord
    set_id = HISTORY_USAGE_INFO
