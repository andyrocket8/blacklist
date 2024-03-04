from typing import Optional
from uuid import UUID

from src.api.di.db_di_routines import get_stream_db_adapter
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import ActionType
from src.service.usage_stream_service import UsageStreamAddService


async def update_usage_bg_task_ns(
    usage_stream_id: UUID, action: ActionType, usage_info: AgentAddressesInfoWithGroup, address_category: Optional[str]
):
    """Task invoked with background task in handle.
    Update actual info (timestamp) of adding and deletion of banned addresses
    Use no session in background task call
    """
    async for stream_db_obj in get_stream_db_adapter():
        usage_add_service = UsageStreamAddService(usage_stream_id, stream_db_obj)
        await usage_add_service.add(action, usage_info, address_category)
