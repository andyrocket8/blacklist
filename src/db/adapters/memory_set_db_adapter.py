import asyncio
import logging
from datetime import datetime as dt_datetime
from datetime import timedelta
from typing import Any
from typing import Generic

from src.db.storages.memory_set_storage import MemorySetStorage
from src.schemas.abstract_types import K

from .base_set_db_adapter import ISetDbAdapter


class MemorySetDbAdapter(ISetDbAdapter[K], Generic[K]):
    """Adapter with ISetDbAdapter interface (without type transformation)"""

    def __init__(self, storage: MemorySetStorage[K, Any]):
        self.__storage: MemorySetStorage[K, Any] = storage

    async def del_set(self, set_id: K) -> int:
        return self.__storage.remove_set(set_id)

    async def copy_set(self, source_set_id: K, target_set_id: K, with_replace: bool = False) -> int:
        return self.__storage.copy_set(source_set_id, target_set_id, with_replace)

    async def exists(self, set_id: K) -> bool:
        return self.__storage.exists(set_id)

    async def set_ttl(self, set_id: K, timeout: int):
        # imitate TTL execution. Add task to EV for manually delete the set
        def del_set_on_ttl(self, set_id: K):
            """Callback for"""
            asyncio.create_task(self.del_set(set_id))
            logging.debug('Started task for set deletion, set id: %s', str(set_id))

        asyncio.get_event_loop().call_later(timeout, del_set_on_ttl, self, set_id)
        logging.debug('Schedule to delete set %s at %s', str(set_id), dt_datetime.now() + timedelta(seconds=timeout))
