import logging
from typing import Optional

from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.usage_schemas import HistoryRecord
from src.schemas.usage_schemas import HistoryRecordInfo
from src.schemas.usage_schemas import SourceRecordInfo
from src.schemas.usage_schemas import UsageRecord

from .usage_db_service import HistoryDBService
from .usage_db_service import UsageDBService


class UsageProcessor:
    """Processor for storing information about address usages"""

    def __init__(self, db_service: UsageDBService):
        self.db_service = db_service

    async def update_usages(self, agent_updated_info: AgentAddressesInfo) -> int:
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
                usage_record = UsageRecord(
                    last_usage_time=agent_updated_info.modification_date,
                    source_records=[
                        SourceRecordInfo(
                            source=agent_updated_info.source_agent, last_info_time=agent_updated_info.modification_date
                        )
                    ],
                )
            else:
                usage_record.last_usage_time = agent_updated_info.modification_date
                # iterate over records and update last usage for certain record
                found: Optional[SourceRecordInfo] = None
                for record in usage_record.source_records:
                    if record.source == agent_updated_info.source_agent:
                        found = record
                        if agent_updated_info.modification_date > found.last_info_time:
                            found.last_info_time = agent_updated_info.modification_date
                        logging.debug(
                            'Update usage statistics for address %s, existing agent %s info',
                            address,
                            agent_updated_info.source_agent,
                        )
                        break
                if found is None:
                    usage_record.source_records.append(
                        SourceRecordInfo(
                            source=agent_updated_info.source_agent, last_info_time=agent_updated_info.modification_date
                        )
                    )
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

    async def update_history(self, agent_deleted_info: AgentAddressesInfo) -> int:
        updated_records = 0
        logging.debug(
            'Update history statistics for %s agent, records count: %d',
            agent_deleted_info.source_agent,
            len(agent_deleted_info.addresses),
        )
        for address in agent_deleted_info.addresses:
            address_str = str(address)
            # get record from usage DB
            address_usage_record = await self.usage_db_service.read_record(address_str)
            usage_records: list[SourceRecordInfo] = []
            if address_usage_record is not None:
                logging.debug(
                    'Use existing usage statistics for address %s, agent %s and '
                    + 'will delete usage info for this address',
                    address,
                    agent_deleted_info.source_agent,
                )
                usage_records = address_usage_record.source_records
            history_record_info_obj = HistoryRecordInfo(
                remover_source=agent_deleted_info.source_agent,
                remove_info_time=agent_deleted_info.modification_date,
                source_records=usage_records,
            )
            # get record from history DB
            history_record_obj = await self.history_db_service.read_record(address_str)
            if history_record_obj is None:
                logging.debug('Empty history for address %s - create new record', address)
                history_record_obj = HistoryRecord(
                    last_update_time=agent_deleted_info.modification_date, history_records=[history_record_info_obj]
                )
            else:
                logging.debug(
                    'Update history for address %s, deleted by agent: %s ', address, agent_deleted_info.source_agent
                )
                history_record_obj.history_records.append(history_record_info_obj)
                history_record_obj.last_update_time = agent_deleted_info.modification_date
            updated_records += await self.history_db_service.write_record(address_str, history_record_obj)
            # delete usage record data
            if len(usage_records):
                logging.debug(
                    'Delete usage info for address %s, agent %s',
                    address,
                    agent_deleted_info.source_agent,
                )
                await self.usage_db_service.delete_record(address_str)

        return updated_records
