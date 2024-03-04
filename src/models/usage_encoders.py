from datetime import datetime as dt_datetime
from json import JSONEncoder


class UsageClassesEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, o):
        if type(o) is dt_datetime:
            return o.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        class_name = o.__class__.__name__
        if class_name == 'UsageRecord':
            raise NotImplementedError('Legacy class. To delete')
        if class_name == 'StreamUsageRecord':
            return o.model_dump(mode='json')
        if class_name == 'HistoryRecordInfo':
            return o.model_dump(mode='json')
        if class_name == 'HistoryRecord':
            return o.model_dump(mode='json')
        if class_name == 'AddressHistoryRecord':
            return o.model_dump(mode='json')

        return JSONEncoder.default(self, o)
