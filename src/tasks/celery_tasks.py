import logging
from asyncio import run as asyncio_run
from typing import Any

from src.celery_app import app as celery_app
from src.db.redis_db import context_async_redis_client
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.usage_schemas import ActionType
from src.service.history_db_service import HistoryDBService
from src.service.usage_db_service import UsageDBService
from src.service.usage_processors import HistoryProcessor
from src.service.usage_processors import UsageProcessor


async def celery_update_history_task_exec(agent_info: AgentAddressesInfo, action_type: ActionType):
    """Async version for celery execution"""
    async with context_async_redis_client('celery') as redis_client_obj:
        usage_db_service: UsageDBService = UsageDBService(redis_client_obj)
        history_db_service: HistoryDBService = HistoryDBService(redis_client_obj)
        history_processor_obj = HistoryProcessor(usage_db_service, history_db_service)
        await history_processor_obj.update_history(agent_info, action_type)


@celery_app.task
def celery_update_history_task(agent_info_dict: dict[str, Any], action_type: ActionType):
    """Wrap to async to re-use asynchronous code. Actually we got zero advantages of
    asyncio because of zero asyncio celery compatibility"""
    agent_info = AgentAddressesInfo(**agent_info_dict)
    logging.debug('Executing celery task: celery_update_history_task, rows count: %d', len(agent_info.addresses))
    asyncio_run(celery_update_history_task_exec(agent_info, action_type))
    logging.debug('Finished celery task: celery_update_history_task, rows count: %d', len(agent_info.addresses))


async def celery_update_usage_info_task_exec(agent_info: AgentAddressesInfo):
    """Async version for celery execution"""
    async with context_async_redis_client('celery') as redis_client_obj:
        usage_db_service: UsageDBService = UsageDBService(redis_client_obj)
        usage_processor_obj = UsageProcessor(usage_db_service)
        await usage_processor_obj.update_usages(agent_info)


@celery_app.task
def celery_update_usage_info_task(agent_info_dict: dict[str, Any]):
    """Wrap to async to re-use asynchronous code. Actually we got zero advantages of
    asyncio because of zero asyncio celery compatibility"""
    agent_info = AgentAddressesInfo(**agent_info_dict)
    logging.debug('Executing celery task: celery_update_usage_info_task, rows count: %d', len(agent_info.addresses))
    asyncio_run(celery_update_usage_info_task_exec(agent_info))
    logging.debug('Finished celery task: celery_update_usage_info_task, rows count: %d', len(agent_info.addresses))
