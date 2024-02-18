import json
from base64 import b64decode
from base64 import b64encode

from src.schemas.set_group_schemas import GroupData

from .transformation import Transformation


class GroupDataTransformer(Transformation[GroupData, str]):
    """Class to perform transformation GroupData <-> str"""

    @classmethod
    def transform_to_storage(cls, value: GroupData) -> str:
        dict_data = {'group_name': value.group_name, 'group_description': value.group_description}
        return b64encode(json.dumps(dict_data).encode()).decode()

    @classmethod
    def transform_from_storage(cls, value: str) -> GroupData:
        dict_data = json.loads(b64decode(value.encode()).decode())
        return GroupData(**dict_data)
