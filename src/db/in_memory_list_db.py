from abc import ABC
from asyncio import sleep
from typing import AsyncGenerator
from typing import Generic
from typing import Optional

from src.models.transformation import TransT
from src.models.transformation import TypeTransT
from src.schemas.abstract_types import Internal

from .abstract_list_db import AbstractListWithTransformDB


class InMemoryListDB(AbstractListWithTransformDB[TransT, Internal], ABC, Generic[TransT, Internal]):
    """Abstract class for storage lists in memory.
    Override transformation methods in sibling classes
    !!! Attention! This class is for testing purposes only. Do not use it in application on any cases.
    """

    storage_type: TypeTransT

    def __init__(self):
        self.__storage: dict[str, list[Internal]] = dict()

    async def create(self, list_name: str):
        """Create list"""
        if list_name not in self.__storage:
            self.__storage[list_name] = list[Internal]()

    async def remove(self, list_name: str):
        """Remove list"""
        if list_name in self.__storage:
            del self.__storage[list_name]

    async def fetch_members(self, list_name: str) -> AsyncGenerator[TransT, None]:
        """Fetch members from list"""
        print(self.__storage)
        processed_list: Optional[list[Internal]] = self.__storage.get(list_name, None)
        if processed_list is not None:
            for value in processed_list:
                yield self.transform_to_user(value)
                await sleep(0)

    async def add_member(self, list_name: str, value: TransT) -> int:
        """Add member to list. If list does not exist it should be created
        Return 1 if member has been actually added otherwise 0
        """
        processed_list: Optional[list[Internal]] = self.__storage.get(list_name, None)
        if processed_list is None:
            # create new list in storage
            processed_list = list[Internal]()
            self.__storage[list_name] = processed_list
        if value not in processed_list:
            processed_list.append(self.transform_to_storage(value))
            return 1
        return 0

    async def del_member(self, list_name: str, value: TransT) -> int:
        processed_list: Optional[list[Internal]] = self.__storage.get(list_name, None)
        transformed_value: Internal = self.transform_to_storage(value)
        if processed_list is not None and transformed_value in processed_list:
            processed_list.remove(transformed_value)
            return 1
        return 0

    def transform_to_storage(self, value: TransT) -> Internal:
        return value.transform_to_storage(value)

    def transform_to_user(self, value: Internal) -> TransT:
        return self.storage_type.transform_from_storage(value)
