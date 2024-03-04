import logging
from typing import Optional

from src.core.config import app_settings
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import ActionType
from src.schemas.usage_schemas import AddressHistoryRecord
from src.schemas.usage_schemas import HistoryRecordInfo
from src.utils import crop_list_tail

from .history_db_service import HistoryDBService


class HistoryProcessor:
    """Processor for storing information about address usages history (after delete)
    Suppose record was not deleted from usage hkey set and this processor should perform it
    """

    def __init__(self, history_db_service: HistoryDBService):
        self.history_db_service = history_db_service

    async def update_history(
        self, agent_action_info: AgentAddressesInfoWithGroup, action_type: ActionType, address_category: str
    ) -> int:
        updated_records = 0
        logging.debug(
            'Update history statistics for %s agent, records count: %d, action type: %s',
            agent_action_info.source_agent,
            len(agent_action_info.addresses),
            action_type,
        )
        for address in agent_action_info.addresses:
            address_str = str(address)
            history_record_obj: Optional[AddressHistoryRecord] = await self.history_db_service.read_record(address_str)
            action_time = agent_action_info.action_time
            history_record_info_obj = HistoryRecordInfo(
                source=agent_action_info.source_agent,
                action_time=action_time,
                action_type=action_type,
                address_category=address_category,
                address_group=agent_action_info.address_group,
            )
            if history_record_obj is None:
                logging.debug('Create history statistics for address %s', address)
                history_record_obj = AddressHistoryRecord(
                    address=address_str,
                    last_update_time=action_time,
                    history_records=crop_list_tail([history_record_info_obj], app_settings.history_depth),
                )
            else:
                logging.debug('Update existing history statistics for address %s', address)
                if action_time > history_record_obj.last_update_time:
                    history_record_obj.last_update_time = action_time
                if app_settings.history_depth is not None:
                    # append record in history_records
                    history_record_obj.history_records.append(history_record_info_obj)
                    history_record_obj.sort()
                    history_record_obj.history_records = crop_list_tail(
                        history_record_obj.history_records, app_settings.history_depth
                    )
                    logging.debug(
                        'History statistics for address %s consists now of %d records',
                        address,
                        len(history_record_obj.history_records),
                    )
                else:
                    history_record_obj.history_records = []
            # commit changes to history db
            updated_records += await self.history_db_service.write_record(address_str, history_record_obj)
        return updated_records
