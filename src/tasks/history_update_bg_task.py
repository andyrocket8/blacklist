from src.schemas.addresses_schemas import AgentAddressesInfo
from src.service.history_db_service import HistoryDBService
from src.service.usage_db_service import UsageDBService
from src.service.usage_processors import HistoryProcessor


async def update_history_bg_task(
    usage_db_service: UsageDBService, history_db_service: HistoryDBService, agent_deleted_info: AgentAddressesInfo
):
    history_processor_obj = HistoryProcessor(usage_db_service, history_db_service)
    await history_processor_obj.update_history(agent_deleted_info)
