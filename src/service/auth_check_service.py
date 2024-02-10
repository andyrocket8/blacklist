from uuid import UUID

from src.db.redis_db import RedisAsyncio
from src.db.redis_set_db import UUIDRedisSetDB
from src.schemas.auth_schemas import AuthCheckResult

from .token_db_services import AdminTokensSetDBService
from .token_db_services import AgentTokensSetDBService


class AuthCheckService:
    def __init__(self, db: RedisAsyncio):
        self._db = db

    async def check_token(self, token: UUID) -> AuthCheckResult:
        agent_db_srv_obj = AgentTokensSetDBService(UUIDRedisSetDB(self._db))
        is_authenticated_user = token in await agent_db_srv_obj.get_records()
        admin_db_srv_obj = AdminTokensSetDBService(UUIDRedisSetDB(self._db))
        is_admin = token in await admin_db_srv_obj.get_records()
        return AuthCheckResult(is_authenticated_user=is_authenticated_user, is_admin=is_admin)
