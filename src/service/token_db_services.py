from uuid import UUID

from src.core.settings import ADMIN_TOKENS_SET_ID
from src.core.settings import AGENT_TOKENS_SET_ID

from .abstract_set_db_entity_service import AbstractSetDBEntityService


class AgentTokensSetDBEntityService(AbstractSetDBEntityService[UUID]):
    class_set_id = AGENT_TOKENS_SET_ID


class AdminTokensSetDBEntityService(AbstractSetDBEntityService[UUID]):
    class_set_id = ADMIN_TOKENS_SET_ID
