from typing import Type

import pytest

from src.db.storages.memory_stream_storage import MemoryStreamTsStorage
from src.models.transformation import Transformation
from src.models.transformation import TransformOneToOne
from src.tests.db.test_stream_db_classes import StockInfoStreamAdapter
from src.tests.db.test_stream_db_classes import StockTestData


class StockInfoStrStreamAdapter(StockInfoStreamAdapter[int, str, int, str]):
    stream_key_transformer: Type[Transformation[int, int]] = TransformOneToOne[int]
    ts_transformer: Type[Transformation[str, str]] = TransformOneToOne[str]


@pytest.mark.asyncio
async def test_memory_stream_storage(stock_test_data: list[StockTestData]):
    """
    During this test we use memory storage for storing streams with int identities, keys as str, and values as bytes
    Also we need adapter to transform StockInfo to dict[str, bytes] while storing and back on restoring
    """

    storage_obj = MemoryStreamTsStorage[int, bytes]()
    memory_stream_adapter = StockInfoStrStreamAdapter(storage_obj)
    # now can make some operations with storage through adapter
    for test_record in stock_test_data:
        await memory_stream_adapter.save_by_timestamp(1, test_record.stock_data, test_record.stock_data.datetime)
    async for record in memory_stream_adapter.fetch_records(1):
        print(record)
