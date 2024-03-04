import logging
from ipaddress import IPv4Address

from src.api.di.db_di_routines import get_history_db_service_for_job
from src.api.di.db_di_routines import get_stream_db_adapter_job
from src.core.settings import STREAM_USAGE_INFO
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import HistoryRecordInfo
from src.service.usage_stream_service import UsageStreamAddService
from src.service.usage_stream_service import UsageStreamReadService


async def migrate_usage_history():
    """Migrate usage history from history statistics
    We read all records from history, order it in time and add to usage history stream with correct timestamps

    """
    async for history_db_service_obj in get_history_db_service_for_job():
        # checking the size of usage history in stream (must be zero)
        async for stream_adapter_db_obj in get_stream_db_adapter_job():
            stream_read_service_obj = UsageStreamReadService(STREAM_USAGE_INFO, stream_adapter_db_obj)
            if await stream_read_service_obj.count() > 0:
                raise ValueError('Usage history must be empty for migration')
            # getting history records
            history_values: list[tuple[HistoryRecordInfo, IPv4Address]] = list()
            async for record in history_db_service_obj.get_records():
                for history_record in record[0].history_records:
                    history_values.append(
                        (
                            history_record,
                            IPv4Address(record[1]),
                        )
                    )
            logging.info('Loaded %d history records', len(history_values))
            history_values = sorted(history_values, key=lambda x: x[0].action_time)
            # writing usage history
            stream_write_service_obj = UsageStreamAddService(STREAM_USAGE_INFO, stream_adapter_db_obj)
            for history_record_info_obj, address in history_values:
                await stream_write_service_obj.add(
                    action=history_record_info_obj.action_type,
                    usage_info=AgentAddressesInfoWithGroup(
                        source_agent=history_record_info_obj.source,
                        action_time=history_record_info_obj.action_time,
                        addresses=[address],
                        address_group=history_record_info_obj.address_group,
                    ),
                    address_category=history_record_info_obj.address_category,
                    timestamp=history_record_info_obj.action_time,
                )
            logging.info('Created %d usage history records', await stream_read_service_obj.count())
