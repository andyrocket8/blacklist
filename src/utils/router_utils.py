# Router common routines


def get_query_params(records_count: int = 10, all_records: bool = False):
    """Common query params"""
    return {'records_count': records_count, 'all_records': all_records}
