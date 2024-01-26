# Ping method router
import logging
from typing import Annotated

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from redis.exceptions import RedisError

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.ping_schemas import PingResponse

api_router = APIRouter()


@api_router.get('', response_model=PingResponse)
async def ping(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    try:
        return {'keys_count': await redis_client_obj.dbsize()}
    except RedisError as e:
        logging.error('On redis ping operation error occurred, details: %s', str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
