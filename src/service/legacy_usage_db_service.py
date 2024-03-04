"""DB Service for usage history processing"""

from typing import Optional
from uuid import UUID

from src.core.settings import ACTIVE_USAGE_INFO
from src.db.storages.redis_db import RedisAsyncio
from src.models.usage_encoders import UsageClassesEncoder
from src.schemas.usage_schemas import UsageRecord
from src.service.abstract_hkey_db_service import AbstractHkeyDBService


class UsageDBService(AbstractHkeyDBService[UsageRecord, UsageClassesEncoder]):
    """Service for current banned addresses usage information"""

    service_type = UsageRecord
    set_id = ACTIVE_USAGE_INFO
    json_encoder = UsageClassesEncoder

    def __init__(self, db: RedisAsyncio, set_id: Optional[UUID] = None):
        super().__init__(db, set_id)
        raise NotImplementedError('Legacy UsageDB service. To delete')
