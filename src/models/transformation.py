from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Type
from typing import TypeVar

from src.schemas.abstract_types import Internal
from src.schemas.abstract_types import T


class Transformation(ABC, Generic[T, Internal]):
    """Interface for transformation data within storage"""

    @staticmethod
    @abstractmethod
    def transform_to_storage(value: T) -> Internal:
        pass

    @classmethod
    @abstractmethod
    def transform_from_storage(cls, value: Internal) -> T:
        pass


# Base abstract class type definition for use in list storages
TransT = TypeVar('TransT', bound=Transformation)
TypeTransT = Type[TransT]
