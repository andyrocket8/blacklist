import logging

from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import UsageRecord

from .usage_db_service import UsageDBService


class UsageProcessor:
    """Processor for storing information about address usages
    TODO migrate to Stream storage (issue-48)
    """

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
