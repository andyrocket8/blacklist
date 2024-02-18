from src.core.settings import HISTORY_USAGE_INFO
from src.schemas.usage_schemas import AddressHistoryRecord
from src.schemas.usage_schemas import UsageClassesEncoder
from src.service.__to_delete.abstract_hkey_db_service import AbstractHkeyDBService


class HistoryDBService(AbstractHkeyDBService[AddressHistoryRecord, UsageClassesEncoder]):
    """Service for current banned addresses usage information"""

    service_type = AddressHistoryRecord
    set_id = HISTORY_USAGE_INFO
    json_encoder = UsageClassesEncoder
