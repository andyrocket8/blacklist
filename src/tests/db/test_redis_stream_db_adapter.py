from typing import AsyncGenerator

import pytest
import pytest_asyncio
from redis.asyncio import Redis as RedisAsyncio

from src.db.adapters.redis_stream_db_adapter import IStreamDbAdapter
from src.db.adapters.redis_stream_db_adapter import RedisStreamDbAdapter
from src.db.base_stream_db import IStreamDb
from src.tests.db.classes_for_stream_db_test import StockInfoDictStreamAdapter
from src.tests.db.classes_for_stream_db_test import StocksTestDataSet

from .tools_for_stream_db_test import perform_stream_db_test


@pytest_asyncio.fixture
async def redis_stream_adapter(redis_connection_pool) -> AsyncGenerator[IStreamDbAdapter, None]:
    """Fixture with str memory set db entity"""
    client_obj = RedisAsyncio.from_pool(redis_connection_pool.connection_pool)
    yield RedisStreamDbAdapter(client_obj)
    # teardown created data
    pass


@pytest.mark.asyncio
async def test_redis_db_adapter(
    stocks_set_test_data: StocksTestDataSet,
    redis_stream_adapter: IStreamDb,
):

    redis_stock_info_stream_adapter = StockInfoDictStreamAdapter(redis_stream_adapter)
    await perform_stream_db_test(stocks_set_test_data, redis_stock_info_stream_adapter, order_on_add=True)
