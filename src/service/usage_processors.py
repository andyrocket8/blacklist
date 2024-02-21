import logging
from typing import Optional

from src.core.config import app_settings
from src.core.settings import HISTORY_PURGE_ON_LAST_DELETE_OPERATION
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import ActionType
from src.schemas.usage_schemas import AddressHistoryRecord
from src.schemas.usage_schemas import HistoryRecordInfo
from src.schemas.usage_schemas import UsageRecord
from src.utils import crop_list_tail

from .history_db_service import HistoryDBService
from .usage_db_service import UsageDBService


class UsageProcessor:
    """Processor for storing information about address usages"""

    def __init__(self, db_service: UsageDBService):
        self.db_service = db_service

    async def update_usages(self, agent_updated_info: AgentAddressesInfoWithGroup) -> int:
        """Update all records in usage set"""
        updated_records = 0
        logging.debug(
            'Update usage statistics for %s agent, records count: %d',
            agent_updated_info.source_agent,
            len(agent_updated_info.addresses),
        )
        for address in agent_updated_info.addresses:
            address_str = str(address)
            usage_record = await self.db_service.read_record(address_str)
            if usage_record is None:
                logging.debug(
                    'Add usage statistics for address %s, agent %s',
                    address,
                    agent_updated_info.source_agent,
                )
                usage_record = UsageRecord(last_usage_time=agent_updated_info.action_time)
            else:
                usage_record.last_usage_time = agent_updated_info.action_time
                # iterate over records and update last usage for certain record
                logging.debug(
                    'Update usage statistics for address %s, new agent %s info',
                    address,
                    agent_updated_info.source_agent,
                )

            updated_records += await self.db_service.write_record(address_str, usage_record)
        return updated_records


class HistoryProcessor:
    """Processor for storing information about address usages history (after delete)
    Suppose record was not deleted from usage hkey set and this processor should perform it
    """

    def __init__(self, usage_db_service: UsageDBService, history_db_service: HistoryDBService):
        self.usage_db_service = usage_db_service
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
            # delete usage record if last operation was deletion.
            # With mixed history for whitelist and blacklist and set groups the further would not work properly!
            if HISTORY_PURGE_ON_LAST_DELETE_OPERATION:
                actions_len = len(history_record_obj.history_records)
                last_action_type = history_record_obj.history_records[actions_len - 1].action_type
                if last_action_type == ActionType.remove_action:
                    logging.debug(
                        'Delete usage info for address %s, agent %s',
                        address,
                        agent_action_info.source_agent,
                    )
                    await self.usage_db_service.delete_record(address_str)
        return updated_records
