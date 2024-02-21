import logging
from uuid import UUID

from src.api.di.db_di_routines import get_set_db_adapter


async def delete_temp_sets_bg(erased_sets: list[UUID]):
    async for set_db_adapter_obj in get_set_db_adapter():
        for eliminated_set in erased_sets:
            await set_db_adapter_obj.del_set(eliminated_set)
            logging.debug('Deleting temporarily set in background, set ID: %s', eliminated_set)
