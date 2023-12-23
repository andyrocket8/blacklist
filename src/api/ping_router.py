# Ping method router
from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter

from src.db.redis_db import RedisAsyncio
from src.db.redis_db import redis_client
from src.schemas.ping_schemas import PingResponse

api_router = APIRouter()


@api_router.get('', response_model=PingResponse)
async def ping(
    redis_client_obj: Annotated[RedisAsyncio, Depends(redis_client)],
):
    return {'keys_count': await redis_client_obj.dbsize()}
