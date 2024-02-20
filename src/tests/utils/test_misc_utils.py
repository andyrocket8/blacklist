from typing import Any

import pytest

from src.utils.misc_utils import crop_list_tail
from src.utils.misc_utils import split_str_list

CROP_LIST_TAIL_DATA: list[dict[str, Any]] = [
    {'source': [1, 2, 3], 'expected_result': [2, 3], 'filter_depth': 2},
    {'source': [1, 2, 3], 'expected_result': [1, 2, 3], 'filter_depth': None},
    {'source': [1, 2, 3, 4], 'expected_result': [], 'filter_depth': 0},
    {'source': [], 'expected_result': [], 'filter_depth': 2},
]


def test_crop_list_tail():
    for step, record in enumerate(CROP_LIST_TAIL_DATA):
        assert (
            crop_list_tail(record['source'], record['filter_depth']) == record['expected_result']
        ), 'Error performing test on step %d' % (step + 1)


@pytest.fixture
def test_split_str_list_data() -> list[tuple[str, list[str]]]:
    return [
        (
            '1,2 ,3, 4,,',
            ['1', '2', '3', '4'],
        ),
        (
            '1,',
            ['1'],
        ),
        (
            '  ',
            [],
        ),
    ]


def test_split_str_list(test_split_str_list_data: list[tuple[str, list[str]]]):
    for test_record in test_split_str_list_data:
        assert split_str_list(test_record[0]) == test_record[1], 'Unexpected test result for "test_split_str_list"'
