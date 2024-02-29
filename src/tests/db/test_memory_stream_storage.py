import pytest

# from src.db.storages.memory_stream_storage import MemoryStreamTsStorage

# from src.tests.db.stream_db_base_tools import StockInfo
# from src.tests.db.stream_db_base_tools import StockTestData


@pytest.mark.asyncio
async def test_memory_stream_storage():
    """
    During this test we use memory storage for storing streams with int identities, keys as str, and values as bytes
    Also we need adapter to transform StockInfo to dict[str, bytes] while storing and back on restoring
    """

    # storage_obj = MemoryStreamTsStorage[int, str, bytes]
    pass
