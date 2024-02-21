from typing import Generic
from typing import Optional
from uuid import UUID

from src.db.base_set_db import ISetDb
from src.schemas.abstract_types import T


class AbstractSetDBService(Generic[T]):
    """Serve operations with abstract classes in Redis database"""

    class_set_id: UUID

    def __init__(self, db: ISetDb[UUID], set_id: Optional[UUID] = None):
        self.__db: ISetDb[UUID] = db
        self.__set_id: UUID = set_id if set_id is not None else self.class_set_id

    async def del_set(self, set_id: UUID) -> int:
        return await self.__db.del_set(set_id)

    async def copy_set(self, source_set_id: UUID, target_set_id: UUID, with_replace: bool = False) -> int:
        return await self.__db.copy_set(source_set_id, target_set_id, with_replace=with_replace)

    async def exists(self, set_id: UUID) -> bool:
        return await self.__db.exists(set_id)

    async def set_ttl(self, set_id: UUID, timeout: int):
        """Set TTL for specified set. After timeout expiration it will be eliminated"""
        await self.__db.set_ttl(set_id, timeout)
