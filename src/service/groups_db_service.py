from typing import Optional
from uuid import UUID
from uuid import uuid4

from fastapi import status
from fastapi.exceptions import HTTPException

from src.core.settings import DEFAULT_GROUP_DESCRIPTION
from src.core.settings import DEFAULT_GROUP_NAME
from src.db.base_hash_db_entity import IHashDbEntity
from src.schemas.set_group_schemas import AddGroupSet
from src.schemas.set_group_schemas import GroupData
from src.schemas.set_group_schemas import GroupSet
from src.schemas.set_group_schemas import UpdateGroupSet


class GroupsDataDbService:
    """Service for interaction with Db Entity with business logic
    On now avoid duplication of logic in interaction with Db - all low level functions are in IHashDbEntity
    """

    def __init__(self, db_entity: IHashDbEntity[UUID, UUID, GroupData], group_hash_id: UUID):
        self.__db_entity = db_entity
        self.__group_hash_id: UUID = group_hash_id

    async def write_group(self, group_id: UUID, group_data: GroupData):
        """Write group data to DB"""
        return await self.__db_entity.write_values(
            self.__group_hash_id,
            (
                (
                    group_id,
                    group_data,
                ),
            ),
        )

    async def read_group(self, group_id: UUID) -> Optional[GroupData]:
        """Read group info from DB"""
        return await self.__db_entity.read_value(self.__group_hash_id, group_id)

    async def read_groups(self) -> list[tuple[UUID, GroupData]]:
        result: list[tuple[UUID, GroupData]] = list()
        async for group_id, group_data in self.__db_entity.fetch_records(self.__group_hash_id):
            result.append(
                (
                    group_id,
                    GroupData(group_name=group_data.group_name, group_description=group_data.group_description),
                )
            )
        return result

    async def delete_group(self, group_id: UUID) -> int:
        return await self.__db_entity.delete_values(self.__group_hash_id, [group_id])


class GroupsDbService:
    """Db Service to help interact helpers with GroupsDataDbService
    Wraps GroupsDataDbService for some extra business logic (default group)
    """

    def __init__(self, db_entity: IHashDbEntity[UUID, UUID, GroupData], group_hash_id: UUID, default_group_id: UUID):
        self.__groups_data_db_srv = GroupsDataDbService(db_entity, group_hash_id)
        self.__default_group_id = default_group_id

    def __get_default_group(self) -> GroupSet:
        return GroupSet(
            group_set_id=self.__default_group_id,
            group_name=DEFAULT_GROUP_NAME,
            group_description=DEFAULT_GROUP_DESCRIPTION,
            default=True,
        )

    async def list_groups(self) -> list[GroupSet]:
        groups_data: list[tuple[UUID, GroupData]] = await self.__groups_data_db_srv.read_groups()
        default_group_value: GroupSet = self.__get_default_group()
        result: list[GroupSet] = list()
        for group_id, value in groups_data:
            if group_id == self.__default_group_id:
                default_group_value = GroupSet(
                    group_set_id=self.__default_group_id,
                    group_name=value.group_name,
                    group_description=value.group_description,
                    default=True,
                )
            else:
                result.append(
                    GroupSet(
                        group_set_id=group_id,
                        group_name=value.group_name,
                        group_description=value.group_description,
                        default=False,
                    )
                )
        result.append(default_group_value)
        return result

    async def get_group(self, group_id: UUID) -> Optional[GroupSet]:
        result: Optional[GroupSet]
        group_data: Optional[GroupData] = await self.__groups_data_db_srv.read_group(group_id)
        if group_id == self.__default_group_id:
            # substitute value with default if default is not changed and saved in hash group
            result = (
                self.__get_default_group()
                if group_data is None
                else GroupSet(
                    group_set_id=group_id,
                    group_name=group_data.group_name,
                    group_description=group_data.group_description,
                    default=True,
                )
            )
        else:
            result = (
                GroupSet(
                    group_set_id=group_id,
                    group_name=group_data.group_name,
                    group_description=group_data.group_description,
                    default=False,
                )
                if group_data is not None
                else None
            )
        return result

    async def add_group(self, group_data: AddGroupSet) -> GroupSet:
        if group_data.group_name == DEFAULT_GROUP_NAME:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Prohibited to add group with default name'
            )
        if await self.group_name_exists(group_data.group_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Already exists group with the same name'
            )
        added_group_id: UUID = uuid4()
        await self.__groups_data_db_srv.write_group(
            added_group_id, GroupData(group_data.group_name, group_data.group_description)
        )
        # read from db

        result: Optional[GroupSet] = await self.get_group(added_group_id)
        assert result is not None, 'Expected added data to storage'
        return result

    async def group_name_exists(self, group_name: str) -> bool:
        groups_data = await self.list_groups()
        return group_name in map(lambda x: x.group_name, groups_data)

    async def update_group(self, updated_group_id: UUID, group_data: UpdateGroupSet) -> GroupSet:
        existing_group_data: Optional[GroupSet] = await self.get_group(updated_group_id)
        if existing_group_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong group id specified in request')
        if group_data.group_name == DEFAULT_GROUP_NAME and updated_group_id != self.__default_group_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Prohibited to set default group name to other group'
            )
        await self.__groups_data_db_srv.write_group(
            updated_group_id, GroupData(group_data.group_name, group_data.group_description)
        )
        result: Optional[GroupSet] = await self.get_group(updated_group_id)
        assert result is not None, 'Expected updated data in storage'
        return result

    async def delete_group(self, group_id: UUID) -> int:
        if self.__default_group_id == group_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Prohibited to delete default group')
        group_data: Optional[GroupSet] = await self.get_group(group_id)
        if group_data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong group id specified in request')
        return await self.__groups_data_db_srv.delete_group(group_id)

    def default_group_id(self):
        """Get default group ID for service"""
        return self.__default_group_id

    async def get_group_by_name(self, group_name: str) -> Optional[GroupSet]:
        """Find group data by group name"""
        groups = await self.list_groups()
        for group in groups:
            if group.group_name == group_name:
                return group
        return None
