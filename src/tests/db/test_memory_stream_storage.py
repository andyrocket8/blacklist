import pytest

from src.db.storages.memory_stream_storage import MemoryStreamTsStorage
from src.tests.db.classes_for_stream_db_test import StockInfoIntStrStreamAdapter
from src.tests.db.classes_for_stream_db_test import StocksTestDataSet

from .tools_for_stream_db_test import perform_stream_db_test


@pytest.mark.asyncio
async def test_memory_stream_storage(stocks_set_test_data: StocksTestDataSet):
    """
    During this test we use memory storage for storing streams with int identities, keys as str, and values as bytes
    Also we need adapter to transform StockInfo to dict[str, bytes] while storing and back on restoring

    Testing the following methods of adapter:
    - save
    - save_by_timestamp
    - delete
    - read
    - fetch_records (straightforward and with filtering)

    """
    storage_obj = MemoryStreamTsStorage[int, bytes]()
    memory_stream_adapter = StockInfoIntStrStreamAdapter(storage_obj)
    await perform_stream_db_test(stocks_set_test_data, memory_stream_adapter)
