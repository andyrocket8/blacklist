import datetime
from functools import partial
from typing import Annotated
from typing import Callable

from pydantic import BaseModel
from pydantic import Field

from src.core.settings import CUR_TZ

now_cur_tz: Callable[[], datetime.datetime] = partial(datetime.datetime.now, tz=CUR_TZ)


class BaseInputSchema(BaseModel):
    source_agent: str
    action_time: Annotated[datetime.datetime, Field(default_factory=now_cur_tz)]
