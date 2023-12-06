# Router common routines


def get_query_params(records_count: int = 10, all_records: bool = False):
    """Common query params"""
    return {'records_count': records_count, 'all_records': all_records}


def get_query_params_with_filter(records_count: int = 10, all_records: bool = False, filter_records: bool = True):
    """Common query params"""
    return {'records_count': records_count, 'all_records': all_records, 'filter_records': filter_records}


def get_query_params_for_download(
    records_count: int = 10, all_records: bool = False, filter_records: bool = True, filename: str = ''
):
    """Query params for download"""
    result = get_query_params_with_filter(records_count, all_records, filter_records)
    result['filename'] = filename
    return result


def get_query_params_with_offset(records_count: int = 10, all_records: bool = False, offset: int = 0):
    """Common query params with offset"""
    return {'records_count': records_count, 'all_records': all_records, 'offset': offset}
