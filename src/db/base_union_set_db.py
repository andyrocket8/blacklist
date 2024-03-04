from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Iterable

from src.schemas.abstract_types import K


class IUnionSetDb(ABC, Generic[K]):
    """Interface for work with united sets. Only perform operations for joining sets"""

    @abstractmethod
    async def union_set(self, set_identities: Iterable[K]) -> K:
        """Union sets and return new set identity"""
        pass
