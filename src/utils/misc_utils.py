# Miscellaneous utilities
from typing import Any
from typing import Optional


def crop_list_tail(list_to_filter: list[Any], filter_depth: Optional[int] = None) -> list[Any]:
    """Crop last <filter_depth> list values. If filter_depth == None - return whole list, 0 means empty list"""
    return (
        list_to_filter[len(list_to_filter) - filter_depth : len(list_to_filter)]
        if filter_depth is not None
        else list_to_filter
    )


def split_str_list(values_comma_separated: str) -> list[str]:
    """parse list of values separated with commas"""
    return [x for x in map(lambda y: y.strip(), values_comma_separated.split(',')) if len(x) > 0]
