from uuid import UUID

from src.models.group_data_transformation import GroupDataTransformer
from src.models.uuid_transformation import UUIDStrTransformer
from src.schemas.set_group_schemas import GroupData

from .base_hash_db_entity_adapter import IHashDbEntityAdapter


class HashDbEntityGroupDataStrAdapter(IHashDbEntityAdapter[UUID, UUID, GroupData, str, str, str]):
    hash_transformer = UUIDStrTransformer
    key_transformer = UUIDStrTransformer
    value_transformer = GroupDataTransformer
