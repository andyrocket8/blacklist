# Router common routines


def get_query_params(records_count: int = 10, all_records: bool = False):
    """Common query params"""
    return {'records_count': records_count, 'all_records': all_records}


def get_query_params_with_filter(records_count: int = 10, all_records: bool = False, filter_records: bool = True):
    """Common query params"""
    return {'records_count': records_count, 'all_records': all_records, 'filter_records': filter_records}
