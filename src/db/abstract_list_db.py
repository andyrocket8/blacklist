from abc import ABC
from abc import abstractmethod
from asyncio import sleep
from typing import AsyncGenerator
from typing import Generic
from typing import cast

from src.models.transformation import TransT
from src.schemas.abstract_types import Internal
from src.schemas.abstract_types import T


class AbstractListDBError(Exception):
    pass


class AbstractListDB(ABC, Generic[T]):
    """Abstract DB Connector with List Features implementation
    Assume that set is created on first write operation
    T: external type of list entities
    """

    @abstractmethod
    async def create(self, list_name: str):
        """Create list"""
        pass

    @abstractmethod
    async def remove(self, list_name: str):
        """Remove list"""
        pass

    @abstractmethod
    async def fetch_members(self, list_name: str) -> AsyncGenerator[T, None]:
        """Fetch members from list"""
        await sleep(0)  # calling awaitable
        yield cast(T, None)  # patch for mypy warnings on incompatible type (do not do this in nested implementations)

    @abstractmethod
    async def add_member(self, list_name: str, value: T) -> int:
        """Add member to list. If list does not exist it should be created
        Return 1 if member has been actually added otherwise 0
        """
        pass

    @abstractmethod
    async def del_member(self, list_name: str, value: T) -> int:
        pass


class AbstractListWithTransformDB(AbstractListDB[TransT], Generic[TransT, Internal]):
    """Abstract DB Connector with List Features implementation
    TransT: external type of list entities with transformation feature
    Internal: internal type of list entities in storage
    """

    @abstractmethod
    def transform_to_user(self, value: Internal) -> TransT:
        """Transform from storage representation to user"""
        pass

    @abstractmethod
    def transform_to_storage(self, value: TransT) -> Internal:
        """Transform from user representation to storage"""
        pass
