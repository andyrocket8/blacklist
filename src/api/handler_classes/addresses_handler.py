# common class for processing addresses handles
from dataclasses import asdict
from typing import Annotated
from typing import Optional

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.api.di.banned_addresses_routines import get_banned_addresses
from src.api.http_auth_wrapper import get_proc_auth_checker
from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import BACKGROUND_ADD_RECORDS
from src.core.settings import BACKGROUND_DELETE_RECORDS
from src.core.settings import HISTORY_USAGE_INFO
from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterIpAddress
from src.db.storages.redis_db import RedisAsyncio
from src.db.storages.redis_db import redis_client
from src.models.query_params_models import CommonQueryParams
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.usage_schemas import ActionType
from src.service.addresses_db_service import BlackListAddressesSetDBService
from src.tasks.celery_tasks import celery_update_history_task
from src.tasks.celery_tasks import celery_update_usage_info_task
from src.tasks.history_update_bg_task import update_history_bg_task_ns
from src.tasks.usage_update_bg_task import update_usage_bg_task_ns

# TODO exclude direct usage of Redis DB provider
addresses_auth_check = get_proc_auth_checker(need_admin_permission=False)


class AddressHandler:
    def __init__(self, address_category: str, address_category_description: str):
        self.__address_category = address_category  # category of address (used in history)
        self.__address_category_description = address_category_description  # used in handler annotations
        self.__router = APIRouter()

    async def addresses_list(
        self,
        redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
        query_params: Annotated[CommonQueryParams, Depends()],
    ):
        # TODO change to universal method
        return await get_banned_addresses(redis_client_obj, asdict(query_params))

    async def save_addresses(
        self,
        agent_info: AgentAddressesInfo,
        redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        # TODO Adopt to universal service
        service_obj = BlackListAddressesSetDBService(
            SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
        )
        added_count = await service_obj.write_records(agent_info.addresses)
        if len(agent_info.addresses) <= BACKGROUND_ADD_RECORDS:
            # run fast tasks in background
            # Update usage information
            background_tasks.add_task(update_usage_bg_task_ns, ACTIVE_USAGE_INFO, agent_info)
            # Update history information
            background_tasks.add_task(
                update_history_bg_task_ns, ACTIVE_USAGE_INFO, HISTORY_USAGE_INFO, agent_info, ActionType.add_action
            )
        else:
            # invoke celery task for update usage and history
            agent_info_dict = agent_info.encode()
            celery_update_usage_info_task.apply_async((agent_info_dict,))
            celery_update_history_task.apply_async(
                (
                    agent_info_dict,
                    ActionType.add_action,
                )
            )

        return AddResponseSchema(added=added_count)

    async def delete_addresses(
        self,
        agent_info: AgentAddressesInfo,
        redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        service_obj = BlackListAddressesSetDBService(
            SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
        )
        deleted_count = await service_obj.del_records(agent_info.addresses)
        if len(agent_info.addresses) <= BACKGROUND_DELETE_RECORDS:
            background_tasks.add_task(
                update_history_bg_task_ns, ACTIVE_USAGE_INFO, HISTORY_USAGE_INFO, agent_info, ActionType.remove_action
            )
        else:
            # invoke celery task for update usage
            agent_info_dict = agent_info.encode()
            celery_update_history_task.apply_async(agent_info_dict, ActionType.remove_action)

        return DeleteResponseSchema(deleted=deleted_count)

    async def count_banned_addresses(
        self,
        redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
    ):
        service_obj = BlackListAddressesSetDBService(
            SetDbEntityStrAdapterIpAddress(RedisSetDbEntityAdapter(redis_client_obj))
        )
        count = await service_obj.count()
        return CountResponseSchema(count=count)

    def router(self) -> APIRouter:
        # decorating handlers methods
        self.__router.get(
            '',
            summary=f'Retrieve {self.__address_category_description} from storage (all or partial)',
            response_model=IpV4AddressList,
        )(self.addresses_list)
        self.__router.post(
            '/add', summary=f'Add {self.__address_category_description} to storage', response_model=AddResponseSchema
        )(self.save_addresses)
        self.__router.post(
            '/delete',
            summary=f'Delete {self.__address_category_description} from storage',
            response_model=DeleteResponseSchema,
        )(self.delete_addresses)
        self.__router.get(
            '/count',
            summary=f'Count {self.__address_category_description} in storage',
            response_model=CountResponseSchema,
        )(self.count_banned_addresses)
        return self.__router
