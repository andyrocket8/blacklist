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


class BaseUnionSetDb(IUnionSetDb[K], Generic[K]):
    """Wrapper for dependency injection"""

    def __init__(self, union_set_db_a: IUnionSetDb[K]):
        self.union_set_db_a: IUnionSetDb[K] = union_set_db_a

    async def union_set(self, set_identities: Iterable[K]) -> K:
        """Union sets and return new set identity"""
        return await self.union_set_db_a.union_set(set_identities)
