import asyncio
from uuid import uuid4

from src.db.abstract_list_db import AbstractListWithTransformDB
from src.db.in_memory_list_db import InMemoryListDB
from src.models.storage_set import StorageSet


class InMemorySetsListDB(InMemoryListDB[StorageSet, str]):
    storage_type = StorageSet


async def fill_storage(storage: AbstractListWithTransformDB[StorageSet, str]):
    await storage.create('pets')
    await storage.add_member('pets', StorageSet('cats', uuid4()))
    await storage.add_member('pets', StorageSet('dogs', uuid4()))
    await storage.add_member('pets', StorageSet('parrots', uuid4()))

    await storage.create('cattle')
    await storage.add_member('cattle', StorageSet('pigs', uuid4()))
    await storage.add_member('cattle', StorageSet('cows', uuid4()))

    await storage.create('predators')
    await storage.add_member('wild', StorageSet('tigers', uuid4()))
    foxes_uuid = uuid4()
    await storage.add_member('wild', StorageSet('foxes', foxes_uuid))
    await storage.add_member('wild', StorageSet('leopards', uuid4()))
    await storage.add_member('wild', StorageSet('bears', uuid4()))
    await storage.add_member('wild', StorageSet('foxes', foxes_uuid))
    await storage.add_member('wild', StorageSet('wolves', uuid4()))


async def get_list_contents(storage: AbstractListWithTransformDB[StorageSet, str], list_name: str) -> list[StorageSet]:
    result: list[StorageSet] = []
    async for value in storage.fetch_members(list_name):
        result.append(value)
    return result


async def main(storage: AbstractListWithTransformDB[StorageSet, str]):
    await fill_storage(storage)
    # await storage.add_member('cattle', StorageSet('cows:12', uuid4()))
    pets = await get_list_contents(storage, 'pets')
    print(pets)
    await storage.del_member('pets', pets[1])
    pets = await get_list_contents(storage, 'pets')
    print(pets)
    print(await get_list_contents(storage, 'cattle'))
    await storage.remove('pets')
    pets = await get_list_contents(storage, 'pets')
    print(pets)
    print(await storage.del_member('pets', StorageSet('cats', uuid4())))


if __name__ == '__main__':
    in_memory_storage = InMemorySetsListDB()
    asyncio.run(main(in_memory_storage))
