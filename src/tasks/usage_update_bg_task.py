from src.schemas.addresses_schemas import AgentAddressesInfo
from src.service.usage_db_service import UsageDBService
from src.service.usage_processors import UsageProcessor


async def update_usage_bg_task(usage_db_service: UsageDBService, agent_info: AgentAddressesInfo):
    """Task invoked with background task in handle.
    Update actual info (timestamp) of adding and deletion of banned addresses"""
    usage_processor_obj = UsageProcessor(usage_db_service)
    await usage_processor_obj.update_usages(agent_info)
