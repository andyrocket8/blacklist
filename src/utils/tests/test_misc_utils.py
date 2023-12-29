from typing import Any

from src.utils.misc_utils import crop_list_tail

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
