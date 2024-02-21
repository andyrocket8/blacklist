from uuid import UUID

from src.db.base_hash_db_entity import IHashDbEntity
from src.schemas.set_group_schemas import GroupData
from src.schemas.set_group_schemas import GroupSet
from src.service.service_db_factories import groups_db_service_factory
from src.utils.misc_utils import split_str_list


class AddressListServiceError(Exception):
    def __init__(self, *args, **kwargs):
        self.status: int = kwargs.get('status', 500)
        super().__init__(*args)


async def retrieve_sets_from_params(
    hash_db_service_obj: IHashDbEntity[UUID, UUID, GroupData], groups_category_name: str, groups_in_param_query: str
) -> list[UUID]:
    """Parse group info and return information of retrieved sets"""

    groups_in_param = split_str_list(groups_in_param_query)
    groups_service_obj = groups_db_service_factory(groups_category_name, hash_db_service_obj)
    parsed_groups: list[GroupSet] = await groups_service_obj.list_groups()
    retrieved_sets: list[UUID] = []
    if groups_in_param:
        for param_group_name in groups_in_param:
            # suppose we have small count of groups ... iterating on groups list
            for group_in_storage in parsed_groups:
                if group_in_storage.group_name == param_group_name:
                    retrieved_sets.append(group_in_storage.group_set_id)
                    break
            else:
                raise ValueError(f'Group with name {param_group_name} is not found in {groups_category_name} groups')
    else:
        # on empty groups list fill all groups
        for group_in_storage in parsed_groups:
            retrieved_sets.append(group_in_storage.group_set_id)
    return retrieved_sets
