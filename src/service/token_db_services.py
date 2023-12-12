from uuid import UUID

from src.core.settings import ADMIN_TOKENS_SET_ID
from src.core.settings import AGENT_TOKENS_SET_ID

from .abstract_set_db_service import AbstractSetDBService


class AgentTokensSetDBService(AbstractSetDBService[UUID]):
    service_type = UUID
    set_id = AGENT_TOKENS_SET_ID


class AdminTokensSetDBService(AbstractSetDBService[UUID]):
    service_type = UUID
    set_id = ADMIN_TOKENS_SET_ID
