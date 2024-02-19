from uuid import UUID

from src.db.storages.redis_db import context_async_redis_client
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.service.usage_db_service import UsageDBService
from src.service.usage_processors import UsageProcessor


async def update_usage_bg_task_ns(usage_set_id: UUID, agent_info: AgentAddressesInfoWithGroup):
    """Task invoked with background task in handle.
    Update actual info (timestamp) of adding and deletion of banned addresses
    Use no session in background task call
    """
    async with context_async_redis_client('background task') as redis_client_obj:
        usage_db_service = UsageDBService(redis_client_obj, usage_set_id)
        usage_processor_obj = UsageProcessor(usage_db_service)
        await usage_processor_obj.update_usages(agent_info)
