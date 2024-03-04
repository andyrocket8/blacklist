from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Type
from typing import TypeVar

from src.schemas.abstract_types import Internal
from src.schemas.abstract_types import T


class Transformation(ABC, Generic[T, Internal]):
    """Interface for transformation data within storage"""

    @classmethod
    @abstractmethod
    def transform_to_storage(cls, value: T) -> Internal:
        pass

    @classmethod
    @abstractmethod
    def transform_from_storage(cls, value: Internal) -> T:
        pass


# Base abstract class type definition for use in storages
TransT = TypeVar('TransT', bound=Transformation)
TypeTransT = Type[TransT]


class TransformOneToOne(Transformation[T, T], Generic[T]):
    @classmethod
    def transform_to_storage(cls, value: T) -> T:
        return value

    @classmethod
    def transform_from_storage(cls, value: T) -> T:
        return value
