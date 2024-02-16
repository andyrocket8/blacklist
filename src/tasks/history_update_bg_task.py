import uuid

from src.db.storages.redis_db import context_async_redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.usage_schemas import ActionType
from src.service.history_db_service import HistoryDBService
from src.service.usage_db_service import UsageDBService
from src.service.usage_processors import HistoryProcessor


async def update_history_bg_task(
    usage_db_service: UsageDBService,
    history_db_service: HistoryDBService,
    agent_info: AgentAddressesInfo,
    action_type: ActionType,
):
    """Task invoked with background task in handle. Update history of adding and deletion of banned addresses"""
    history_processor_obj = HistoryProcessor(usage_db_service, history_db_service)
    await history_processor_obj.update_history(agent_info, action_type)


async def update_history_bg_task_ns(
    usage_set_id: uuid.UUID,
    history_set_id: uuid.UUID,
    agent_info: AgentAddressesInfo,
    action_type: ActionType,
):
    """Task invoked with background task in handle.
    Update history of adding and deletion of banned addresses
    Use no dependency connection in background task call
    """
    async with context_async_redis_client('background task') as redis_client_obj:
        usage_db_service = UsageDBService(redis_client_obj, usage_set_id)
        history_db_service: HistoryDBService = HistoryDBService(redis_client_obj, history_set_id)
        history_processor_obj = HistoryProcessor(usage_db_service, history_db_service)
        await history_processor_obj.update_history(agent_info, action_type)
