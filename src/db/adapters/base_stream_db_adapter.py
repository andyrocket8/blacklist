from abc import ABC

from src.db.base_stream_db import IK
from src.db.base_stream_db import SK
from src.db.base_stream_db import IStreamDb
from src.schemas.abstract_types import K
from src.schemas.abstract_types import V


class IStreamDbAdapter(IStreamDb[SK, IK, K, V], ABC):
    """Base interface class for all stream adapters"""

    pass
