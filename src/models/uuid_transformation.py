from uuid import UUID

from .transformation import Transformation


class UUIDStrTransformer(Transformation[UUID, str]):
    """Transformation from UUID to internal str for Redis"""

    @classmethod
    def transform_to_storage(cls, value: UUID) -> str:
        return str(value)

    @classmethod
    def transform_from_storage(cls, value: str) -> UUID:
        return UUID(value)
