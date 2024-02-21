from uuid import UUID
from uuid import uuid4

from src.models.uuid_transformation import UUIDStrTransformer

from .base_union_set_db_adapter import BaseUnionSetDbTransformAdapter


def generate_str_uuid() -> str:
    return str(uuid4())


class UnionSetDbTransformUUIDAdapter(BaseUnionSetDbTransformAdapter[UUID, str]):
    key_transformer = UUIDStrTransformer
