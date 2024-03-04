import logging
from asyncio import run as asyncio_run
from asyncio import sleep as a_sleep
from typing import Any
from typing import Optional
from uuid import UUID

from src.api.di.db_di_routines import get_stream_db_adapter_job
from src.celery_app import app as celery_app
from src.db.storages.redis_db import context_async_redis_client
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.usage_schemas import ActionType
from src.service.history_db_service import HistoryDBService
from src.service.history_processors import HistoryProcessor
from src.service.usage_stream_service import UsageStreamAddService


async def celery_update_history_task_exec(
    agent_info: AgentAddressesInfoWithGroup, action_type: ActionType, address_category: str
):
    """Async version for celery execution"""
    async with context_async_redis_client('celery') as redis_client_obj:
        history_db_service: HistoryDBService = HistoryDBService(redis_client_obj)
        history_processor_obj = HistoryProcessor(history_db_service)
        await history_processor_obj.update_history(agent_info, action_type, address_category)


@celery_app.task
def celery_update_history_task(agent_info_dict: dict[str, Any], action_type: ActionType, address_category: str):
    """Wrap to async to re-use asynchronous code. Actually we got zero advantages of
    asyncio because of zero asyncio celery compatibility"""
    agent_info = AgentAddressesInfoWithGroup(**agent_info_dict)
    logging.debug('Executing celery task: celery_update_history_task, rows count: %d', len(agent_info.addresses))
    asyncio_run(celery_update_history_task_exec(agent_info, action_type, address_category))
    logging.debug('Finished celery task: celery_update_history_task, rows count: %d', len(agent_info.addresses))


async def celery_update_usage_info_task_exec(
    usage_stream_id: UUID, action: ActionType, usage_info: AgentAddressesInfoWithGroup, address_category: Optional[str]
):
    """Async version for celery execution"""
    async for stream_db_obj in get_stream_db_adapter_job('Stream usage celery task'):
        usage_add_service = UsageStreamAddService(usage_stream_id, stream_db_obj)
        await usage_add_service.add(action, usage_info, address_category)
        await a_sleep(0)


@celery_app.task
def celery_update_usage_info_task(
    usage_stream_id: UUID, action: ActionType, agent_info_dict: dict[str, Any], address_category: Optional[str]
):
    """Wrap to async to re-use asynchronous code. Actually we got zero advantages of
    asyncio because of zero asyncio celery compatibility"""
    agent_info = AgentAddressesInfoWithGroup(**agent_info_dict)
    logging.debug('Executing celery task: celery_update_usage_info_task, rows count: %d', len(agent_info.addresses))
    asyncio_run(celery_update_usage_info_task_exec(usage_stream_id, action, agent_info, address_category))
    logging.debug('Finished celery task: celery_update_usage_info_task, rows count: %d', len(agent_info.addresses))
