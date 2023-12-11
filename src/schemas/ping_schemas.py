from pydantic import BaseModel


class PingResponse(BaseModel):
    keys_count: int
