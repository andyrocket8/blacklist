from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Iterable

from src.schemas.abstract_types import K


class IUnionSetDb(ABC, Generic[K]):
    """Interface for work with united sets
    Extends ISetDb to perform also basic operations with sets
    """

    @abstractmethod
    async def union_set(self, set_identities: Iterable[K]) -> K:
        """Union sets and return new set identity"""
        pass


class BaseUnionSetDb(IUnionSetDb[K]):
    """Base Union Set for interaction with DB Adapters"""

    def __init__(self, set_db_adapter: IUnionSetDb[K]):
        self.__set_db_adapter: IUnionSetDb[K] = set_db_adapter

    async def union_set(self, set_identities: Iterable[K]) -> K:
        """Union sets and return new set identity"""
        return await self.__set_db_adapter.union_set(set_identities)
