from uuid import UUID

from pydantic import BaseModel


class GroupSet(BaseModel):
    """DTO for group sets"""

    group_name: str  # group name
    group_set_id: UUID  # group set ID (as in Redis storage)


class AddGroupSet(BaseModel):
    """DTO for adding group set"""

    group_name: str  # group set name


class UpdateGroupSet(BaseModel):
    """DTO for adding group set"""

    group_name: str  # group name
