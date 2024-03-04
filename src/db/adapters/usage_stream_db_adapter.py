from typing import Generic
from typing import Type
from uuid import UUID

from src.db.base_stream_db import IKInternal
from src.db.base_stream_db import SKInternal
from src.models.transformation import Transformation
from src.models.transformation import TransformOneToOne
from src.models.usage_transformation import SURDictTransformation
from src.models.uuid_transformation import UUIDStrTransformer
from src.schemas.abstract_types import Internal
from src.schemas.usage_schemas import StreamUsageRecord

from .base_stream_db_adapter import BaseStreamDbAdapter


class UsageStreamDbAdapter(
    BaseStreamDbAdapter[UUID, str, StreamUsageRecord, SKInternal, IKInternal, Internal],
    Generic[SKInternal, IKInternal, Internal],
):

    stream_key_transformer: Type[Transformation[UUID, SKInternal]]  # transformer for streams
    ts_transformer: Type[Transformation[str, IKInternal]]  # transformer for timestamp identity
    value_transformer: Type[Transformation[StreamUsageRecord, Internal]]  # transformer for value


class UsageStreamRedisAdapter(UsageStreamDbAdapter[str, str, dict[str, str]]):
    stream_key_transformer = UUIDStrTransformer
    ts_transformer = TransformOneToOne[str]
    value_transformer: Type[Transformation[StreamUsageRecord, dict[str, str]]] = SURDictTransformation
