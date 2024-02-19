# common class for processing addresses handles
from typing import Annotated
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.api.di.db_di_routines import address_with_groups_db_service_adapter
from src.api.http_auth_wrapper import get_proc_auth_checker
from src.core.settings import ACTIVE_USAGE_INFO
from src.core.settings import ALLOWED_ADDRESSES_CATEGORY_NAME
from src.core.settings import BACKGROUND_ADD_RECORDS
from src.core.settings import BACKGROUND_DELETE_RECORDS
from src.core.settings import BANNED_ADDRESSES_CATEGORY_NAME
from src.core.settings import HISTORY_USAGE_INFO
from src.models.query_params_models import CommonQueryParams
from src.models.query_params_models import CountAddress
from src.schemas.addresses_schemas import AgentAddressesInfoWithGroup
from src.schemas.addresses_schemas import IpV4AddressList
from src.schemas.common_response_schemas import AddResponseSchema
from src.schemas.common_response_schemas import CountResponseSchema
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.set_group_schemas import GroupSet
from src.schemas.usage_schemas import ActionType
from src.service.abstract_set_db_service import AbstractSetDBService
from src.service.groups_db_service import GroupsDbService
from src.service.service_db_factories import ServiceWithGroupDbAdapters
from src.service.service_db_factories import any_addresses_db_service_factory
from src.service.service_db_factories import groups_db_service_factory
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

    @staticmethod
    async def get_group_id(address_group_name: Optional[str], groups_service_obj: GroupsDbService) -> UUID:
        if address_group_name is None:
            group_set_id = groups_service_obj.default_group_id()
        else:
            group_set_obj: Optional[GroupSet] = await groups_service_obj.get_group_by_name(address_group_name)
            if group_set_obj is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f'Wrong group name specified: {address_group_name}'
                )
            group_set_id = group_set_obj.group_set_id
        return group_set_id

    async def get_service_and_set(
        self, db_service_adapter: ServiceWithGroupDbAdapters, group_name: Optional[str]
    ) -> tuple[GroupsDbService, AbstractSetDBService, UUID]:
        groups_service_obj = groups_db_service_factory(
            self.__address_category, db_service_adapter.db_hash_service_adapter
        )
        group_set_id = await self.get_group_id(group_name, groups_service_obj)
        service_obj = any_addresses_db_service_factory(
            group_set_id,
            db_service_adapter.db_service_adapter,
        )
        return groups_service_obj, service_obj, group_set_id

    async def addresses_list(
        self,
        db_service_adapter: Annotated[ServiceWithGroupDbAdapters, Depends(address_with_groups_db_service_adapter)],
        query_params: Annotated[CommonQueryParams, Depends()],
    ):
        _hash_service_obj, service_obj, _group_set_id = await self.get_service_and_set(
            db_service_adapter, query_params.address_group
        )
        return await service_obj.get_records(
            records_count=query_params.records_count, all_records=query_params.all_records
        )

    async def save_addresses(
        self,
        agent_info: AgentAddressesInfoWithGroup,
        db_service_adapter: Annotated[ServiceWithGroupDbAdapters, Depends(address_with_groups_db_service_adapter)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        _hash_service_obj, service_obj, _group_set_id = await self.get_service_and_set(
            db_service_adapter, agent_info.address_group
        )

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
        agent_info: AgentAddressesInfoWithGroup,
        db_service_adapter: Annotated[ServiceWithGroupDbAdapters, Depends(address_with_groups_db_service_adapter)],
        background_tasks: BackgroundTasks,
        auth: Optional[HTTPAuthorizationCredentials] = Depends(addresses_auth_check),  # noqa: B008
    ):
        _hash_service_obj, service_obj, _group_set_id = await self.get_service_and_set(
            db_service_adapter, agent_info.address_group
        )
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
        query_params: Annotated[CountAddress, Depends()],
        db_service_adapter: Annotated[ServiceWithGroupDbAdapters, Depends(address_with_groups_db_service_adapter)],
    ):
        _hash_service_obj, service_obj, _group_set_id = await self.get_service_and_set(
            db_service_adapter, query_params.address_group
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
