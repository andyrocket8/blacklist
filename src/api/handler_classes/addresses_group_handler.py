from typing import Annotated
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from src.api.di.db_di_routines import groups_db_service_adapter
from src.db.base_hash_db_entity import IHashDbEntity
from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.set_group_schemas import AddGroupSet
from src.schemas.set_group_schemas import GroupSet
from src.schemas.set_group_schemas import UpdateGroupSet
from src.service.groups_db_service import GroupsDbService
from src.service.service_db_factories import groups_db_service_factory


class AddressesGroupHandler:
    """Class for aggregating group classes"""

    def __init__(self, group_category: str):
        self.group_category: str = group_category
        self.__router = APIRouter()

    def __get_service_obj(self, db_service_adapter: IHashDbEntity) -> GroupsDbService:
        """Obtain service class from factory"""
        return groups_db_service_factory(self.group_category, db_service_adapter)

    async def group_list(
        self,
        db_service_adapter: Annotated[IHashDbEntity, Depends(groups_db_service_adapter)],
    ) -> list[GroupSet]:
        db_service = self.__get_service_obj(db_service_adapter)
        return await db_service.list_groups()

    async def get_group(
        self,
        group_set_id: UUID,
        db_service_adapter: Annotated[IHashDbEntity, Depends(groups_db_service_adapter)],
    ) -> Union[GroupSet | dict]:
        db_service = self.__get_service_obj(db_service_adapter)
        result = await db_service.get_group(group_set_id)
        return dict() if result is None else result

    async def add_group(
        self,
        group_data: AddGroupSet,
        db_service_adapter: Annotated[IHashDbEntity, Depends(groups_db_service_adapter)],
    ) -> GroupSet:
        db_service = self.__get_service_obj(db_service_adapter)
        return await db_service.add_group(group_data)

    async def delete_group(
        self,
        group_set_id: UUID,
        db_service_adapter: Annotated[IHashDbEntity, Depends(groups_db_service_adapter)],
    ) -> DeleteResponseSchema:
        db_service = self.__get_service_obj(db_service_adapter)
        return DeleteResponseSchema(deleted=await db_service.delete_group(group_set_id))

    async def update_group(
        self,
        group_set_id: UUID,
        group_data: UpdateGroupSet,
        db_service_adapter: Annotated[IHashDbEntity, Depends(groups_db_service_adapter)],
    ):
        db_service = self.__get_service_obj(db_service_adapter)
        return await db_service.update_group(group_set_id, group_data)

    def router(self) -> APIRouter:
        # decorating handlers methods
        self.__router.get('/', response_model=list[GroupSet], summary=f'List {self.group_category} groups')(
            self.group_list
        )
        self.__router.post('/', response_model=GroupSet, summary=f'Add group of {self.group_category} groups')(
            self.add_group
        )
        self.__router.get(
            '/{group_set_id}', response_model=Union[GroupSet, dict], summary=f'Get {self.group_category} group'
        )(self.get_group)
        self.__router.put('/{group_set_id}', response_model=GroupSet, summary=f'Change {self.group_category} group')(
            self.update_group
        )
        self.__router.delete(
            '/{group_set_id}', response_model=DeleteResponseSchema, summary=f'Remove {self.group_category} group'
        )(self.delete_group)
        return self.__router
