from src.core.settings import HISTORY_USAGE_INFO
from src.schemas.usage_schemas import HistoryRecord
from src.schemas.usage_schemas import UsageClassesEncoder

from .abstract_hkey_db_service import AbstractHkeyDBService


class HistoryDBService(AbstractHkeyDBService[HistoryRecord, UsageClassesEncoder]):
    """Service for current banned addresses usage information"""

    service_type = HistoryRecord
    set_id = HISTORY_USAGE_INFO
    json_encoder = UsageClassesEncoder
