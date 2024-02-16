from uuid import UUID

from fastapi import APIRouter

from src.schemas.common_response_schemas import DeleteResponseSchema
from src.schemas.set_group_schemas import AddGroupSet
from src.schemas.set_group_schemas import GroupSet
from src.schemas.set_group_schemas import UpdateGroupSet


class AddressesGroup:
    """Class for aggregating group classes"""

    def __init__(self, group_category: str):
        self.group_category = group_category
        self.__router = APIRouter()

    async def group_list(self):
        return [
            {'group_name': 'default', 'group_set_id': 'fd1f939c-345f-434f-8e21-2387313ac029'},
        ]

    async def add_group(self, group_data: AddGroupSet):
        pass

    async def delete_group(self, group_set_id: UUID):
        pass

    async def update_group(self, group_set_id: str, group_data: UpdateGroupSet):
        pass

    def router(self) -> APIRouter:
        # decorating handlers methods
        self.__router.get('/', response_model=list[GroupSet], summary=f'List {self.group_category} groups')(
            self.group_list
        )
        self.__router.post('/', response_model=GroupSet, summary=f'Add group of {self.group_category} groups')(
            self.add_group
        )
        self.__router.put('/{group_set_id}', response_model=GroupSet, summary=f'Change {self.group_category} group')(
            self.update_group
        )
        self.__router.delete(
            '/{group_set_id}', response_model=DeleteResponseSchema, summary=f'Remove {self.group_category} group'
        )(self.delete_group)
        return self.__router
