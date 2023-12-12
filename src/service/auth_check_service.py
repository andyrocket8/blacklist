import uuid

from src.db.redis_db import RedisAsyncio
from src.schemas.auth_schemas import AuthCheckResult

from .token_db_services import AdminTokensSetDBService
from .token_db_services import AgentTokensSetDBService


class AuthCheckService:
    def __init__(self, db: RedisAsyncio):
        self._db = db

    async def check_token(self, token: uuid.UUID) -> AuthCheckResult:
        agent_db_srv_obj = AgentTokensSetDBService(self._db)
        is_authenticated_user = token in await agent_db_srv_obj.get_records()
        admin_db_srv_obj = AdminTokensSetDBService(self._db)
        is_admin = token in await admin_db_srv_obj.get_records()
        return AuthCheckResult(is_authenticated_user=is_authenticated_user, is_admin=is_admin)
