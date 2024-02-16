from uuid import UUID

from src.db.adapters.redis_set_db_entity_adapter import RedisSetDbEntityAdapter
from src.db.adapters.set_db_entity_str_adapter import SetDbEntityStrAdapterUUID
from src.db.storages.redis_db import RedisAsyncio
from src.schemas.auth_schemas import AuthCheckResult

from .token_db_services import AdminTokensSetDBService
from .token_db_services import AgentTokensSetDBService


class AuthCheckService:
    def __init__(self, db: RedisAsyncio):
        self._db = db

    async def check_token(self, token: UUID) -> AuthCheckResult:
        agent_db_srv_obj = AgentTokensSetDBService(SetDbEntityStrAdapterUUID(RedisSetDbEntityAdapter(self._db)))
        is_authenticated_user = token in await agent_db_srv_obj.get_records()
        admin_db_srv_obj = AdminTokensSetDBService(SetDbEntityStrAdapterUUID(RedisSetDbEntityAdapter(self._db)))
        is_admin = token in await admin_db_srv_obj.get_records()
        return AuthCheckResult(is_authenticated_user=is_authenticated_user, is_admin=is_admin)
