from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel


class GroupSet(BaseModel):
    """DTO for group sets"""

    group_set_id: UUID  # group set ID (as in Redis storage)
    group_name: str  # group name
    group_description: str  # group description
    default: bool  # sign of default (under the hood) group (can't be deleted)


class AddGroupSet(BaseModel):
    """DTO for adding group set"""

    group_name: str  # group set name
    group_description: str  # group description


class UpdateGroupSet(BaseModel):
    """DTO for adding group set"""

    group_name: str  # group name
    group_description: str  # group description


@dataclass
class GroupData:
    """Class for internal storage as hash value"""

    group_name: str
    group_description: str
