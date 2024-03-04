import random
from asyncio import sleep as a_sleep
from dataclasses import dataclass
from typing import Union

# from src.tests.db.classes_for_stream_db_test import StockInfoIntStrStreamAdapter
from src.db.adapters.base_stream_db_adapter import BaseStreamDbAdapter
from src.tests.db.classes_for_stream_db_test import StockInfo
from src.tests.db.classes_for_stream_db_test import StocksTestDataSet


@dataclass
class SetDataRecord:
    set_id: int
    timestamp: str
    data: StockInfo


async def perform_stream_db_test(
    stocks_set_test_data: StocksTestDataSet,
    stream_adapter: Union[
        BaseStreamDbAdapter[int, str, StockInfo, int, str, bytes],
        BaseStreamDbAdapter[int, str, StockInfo, str, str, dict[str, str]],
    ],
    order_on_add: bool = False,
):
    """
    During this test we use arbitrary storage for storing streams with int identities, keys as str, and values as bytes
    Also we need adapter to transform StockInfo to bytes or dict[str, bytes] while storing and back on restoring

    Testing the following methods of adapter:
    - save
    - save_by_timestamp
    - delete
    - read
    - fetch_records (straightforward and with filtering)

    """
    # obtain the random id for set 1
    set_1: int = random.randint(10, 20)
    # obtain the random id for set 2
    set_2: int = random.randint(30, 40)
    print(set_1, set_2)
    # now can make some operations with storage through adapter
    stock_test_data = stocks_set_test_data.stock_test_list
    # add data with 'save_by_timestamp', expecting sorting of added data by timestamp index
    for test_record in sorted(stock_test_data, key=lambda x: x.order) if order_on_add else stock_test_data:
        await stream_adapter.save_by_timestamp(set_1, test_record.stock_data, test_record.stock_data.datetime)
    # checking filtering in fetch_records, iterating over test sets
    for test_set in stocks_set_test_data.check_filter_data_list:
        fetched_records: list[SetDataRecord] = list()
        async for record in stream_adapter.fetch_records(set_1, start_ts=test_set.start_date, end_ts=test_set.end_date):
            fetched_records.append(SetDataRecord(set_1, record[0], record[1]))
        # checking count of fetched records
        assert (
            len(fetched_records) == test_set.expected_records_count
        ), 'Expecting count of fetched records to be the same as expected'
        # checking of first matching record
        assert (
            fetched_records[0].data == test_set.expected_first_record.stock_data
        ), 'Expecting first fetched record to be the same as expected'
        # checking of last matching record
        assert (
            fetched_records[-1].data == test_set.expected_last_record.stock_data
        ), 'Expecting Last fetched record to be the same as expected'

    records: list[SetDataRecord] = list()
    async for record in stream_adapter.fetch_records(set_1):
        records.append(SetDataRecord(set_1, record[0], record[1]))
    # add the same data to another set, with ordering as in list
    for test_record in stock_test_data:
        await stream_adapter.save(set_2, test_record.stock_data)
        await a_sleep(0.01)  # some delay here
    # checking the contents of set no 2 with the test set data
    counter = 0
    for storage_record, test_set_record in zip(
        [storage_record async for storage_record in stream_adapter.fetch_records(set_2)], stock_test_data
    ):
        assert (
            storage_record[1] == test_set_record.stock_data
        ), f'Expecting stored record be the same as in unordered test set, iteration: {counter}'
        records.append(SetDataRecord(set_2, storage_record[0], storage_record[1]))
        counter += 1
    assert counter == len(stock_test_data), 'Expected all records of test set to be in storage in set 2'
    for record_data in records:
        print(await stream_adapter.read(record_data.set_id, record_data.timestamp))
    # testing length of streams
    assert await stream_adapter.count(set_1) == len(
        stock_test_data
    ), f'Expecting the length of stream with id: {set_1} equal to test data set length'
    assert await stream_adapter.count(set_2) == len(
        stock_test_data
    ), f'Expecting the length of stream with id: {set_2} equal to test data set length'
    assert (await stream_adapter.delete(set_1, map(lambda x: x.timestamp, records))) == len(
        stock_test_data
    ), 'Expecting to delete only existing records in set 1'
    assert (await stream_adapter.delete(set_2, map(lambda x: x.timestamp, records))) == len(
        stock_test_data
    ), 'Expecting to delete only existing records in set 2'
    # assure the data has been properly cleaned from storage
    assert (
        len([storage_record async for storage_record in stream_adapter.fetch_records(set_1)]) == 0
    ), 'Set 1 must be cleared on end of the test'
    assert (
        len([storage_record async for storage_record in stream_adapter.fetch_records(set_2)]) == 0
    ), 'Set 2 must be cleared on end of the test'
