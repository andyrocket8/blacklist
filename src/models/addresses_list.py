from dataclasses import dataclass
from uuid import UUID

from .transformation import Transformation


@dataclass
class StorageSet(Transformation['StorageSet', str]):
    """Simple 'to str' dataclass transformation implementation, avoid ':' in set name
    Suitable for use with Redis lists
    """

    set_name: str
    set_id: UUID

    @staticmethod
    def transform_to_storage(value: 'StorageSet') -> str:
        assert ':' not in value.set_name, f'Not allowed : in passed set name {value.set_name!r}'
        return f'{value.set_name}:{str(value.set_id)}'

    @classmethod
    def transform_from_storage(cls, value: str) -> 'StorageSet':
        set_name, set_id = value.split(':')
        return StorageSet(set_name, UUID(set_id))
