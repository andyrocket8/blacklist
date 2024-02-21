import logging
from typing import Callable
from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from src.core.config import app_settings
from src.db.storages.redis_db import context_async_redis_client
from src.service.auth_check_service import AuthCheckService

http_bearer_obj = HTTPBearer(auto_error=True)


def get_proc_auth_checker(need_admin_permission: bool = False) -> Callable:
    async def stub_auth_func():
        return None

    async def get_user_data(
        auth: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer_obj),  # noqa: B008
    ):
        assert auth is not None, 'Expected filled auth attribute here'
        token = auth.credentials
        # check whether token is UUID
        try:
            auth_token = UUID(token)
        except ValueError:
            error_msg = f'Malformed auth token: {token}'
            logging.error(error_msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg) from None
        async with context_async_redis_client('auth') as db:
            auth_check = await AuthCheckService(db).check_token(auth_token)
            if need_admin_permission and not auth_check.is_admin:
                error_msg = 'Authentication failed: admin rights needed'
                logging.error(error_msg)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg) from None
            if not auth_check.is_authenticated_user and not auth_check.is_admin:
                error_msg = 'Authentication failed'
                logging.error(error_msg)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_msg) from None
            logging.debug(
                'Successfully authenticate user with %s permissions',
                'ordinary' if auth_check.is_authenticated_user else 'administrative',
            )

    if not app_settings.use_authorization:
        return stub_auth_func

    return get_user_data
