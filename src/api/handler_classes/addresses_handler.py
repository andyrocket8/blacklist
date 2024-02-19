# common class for processing addresses handles
from typing import Annotated
from typing import Optional

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.api.di.db_di_routines import address_db_service_adapter
from src.api.http_auth_wrapper import get_proc_auth_checker
from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import ALLOWED_ADDRESSES_CATEGORY_NAME
from src.core.settings import BACKGROUND_ADD_RECORDS
from src.core.settings import BACKGROUND_DELETE_RECORDS
from src.core.settings import BANNED_ADDRESSES_CATEGORY_NAME
from src.core.settings import HISTORY_USAGE_INFO
from src.db.base_set_db_entity import ISetDbEntity
from src.models.query_params_models import CommonQueryParams
from src.schemas.addresses_schemas import AgentAddressesInfo
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.usage_schemas import ActionType
from src.service.service_db_factories import addresses_db_service_factory
from src.tasks.celery_tasks import celery_update_history_task
from src.tasks.celery_tasks import celery_update_usage_info_task
from src.tasks.history_update_bg_task import update_history_bg_task_ns
from src.tasks.usage_update_bg_task import update_usage_bg_task_ns

# TODO exclude direct usage of Redis DB provider
addresses_auth_check = get_proc_auth_checker(need_admin_permission=False)


class AddressHandler:
    def __init__(self, address_category: str, address_category_description: str):
        assert address_category in (
            BANNED_ADDRESSES_CATEGORY_NAME,
            ALLOWED_ADDRESSES_CATEGORY_NAME,
        ), 'Wrong address category name supplied'
        self.__address_category = address_category  # category of address (used in history)
        self.__address_category_description = address_category_description  # used in handler annotations
        self.__router = APIRouter()

    async def addresses_list(
        self,
        db_service_adapter: Annotated[ISetDbEntity, Depends(address_db_service_adapter)],
        query_params: Annotated[CommonQueryParams, Depends()],
    ):
        service_obj = addresses_db_service_factory(self.__address_category, db_service_adapter)
        return await service_obj.get_records(
            records_count=query_params.records_count, all_records=query_params.all_records
        )

    async def save_addresses(
        self,
        agent_info: AgentAddressesInfo,
        db_service_adapter: Annotated[ISetDbEntity, Depends(address_db_service_adapter)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        service_obj = addresses_db_service_factory(self.__address_category, db_service_adapter)
        added_count = await service_obj.write_records(agent_info.addresses)
        if len(agent_info.addresses) <= BACKGROUND_ADD_RECORDS:
            # run fast tasks in background
            # Update usage information
            background_tasks.add_task(update_usage_bg_task_ns, ACTIVE_USAGE_INFO, agent_info)
            # Update history information
            background_tasks.add_task(
                update_history_bg_task_ns,
                ACTIVE_USAGE_INFO,
                HISTORY_USAGE_INFO,
                agent_info,
                ActionType.add_action,
                self.__address_category,
            )
        else:
            # invoke celery task for update usage and history
            agent_info_dict = agent_info.encode()
            celery_update_usage_info_task.apply_async((agent_info_dict,))
            celery_update_history_task.apply_async(
                (
                    agent_info_dict,
                    ActionType.add_action,
                    self.__address_category,
                )
            )

        return AddResponseSchema(added=added_count)

    async def delete_addresses(
        self,
        agent_info: AgentAddressesInfo,
        db_service_adapter: Annotated[ISetDbEntity, Depends(address_db_service_adapter)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        service_obj = addresses_db_service_factory(self.__address_category, db_service_adapter)
        deleted_count = await service_obj.del_records(agent_info.addresses)
        if len(agent_info.addresses) <= BACKGROUND_DELETE_RECORDS:
            # TODO Adopt background services
            background_tasks.add_task(
                update_history_bg_task_ns,
                ACTIVE_USAGE_INFO,
                HISTORY_USAGE_INFO,
                agent_info,
                ActionType.remove_action,
                self.__address_category,
            )
        else:
            # invoke celery task for update usage
            # TODO Adopt celery tasks
            agent_info_dict = agent_info.encode()
            celery_update_history_task.apply_async(agent_info_dict, ActionType.remove_action, self.__address_category)

        return DeleteResponseSchema(deleted=deleted_count)

    async def count_banned_addresses(
        self,
        db_service_adapter: Annotated[ISetDbEntity, Depends(address_db_service_adapter)],
    ):
        service_obj = addresses_db_service_factory(self.__address_category, db_service_adapter)
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
