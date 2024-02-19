from uuid import UUID

from src.models.uuid_transformation import UUIDStrTransformer

from .base_set_db_adapter import BaseSetDbAdapter


class SetDbStrAdapterUUID(BaseSetDbAdapter[UUID, str]):
    """Set management adapter with UUID -> str transformer"""

    key_transform = UUIDStrTransformer
