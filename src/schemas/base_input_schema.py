from pydantic import BaseModel


class BaseInputSchema(BaseModel):
    source_agent: str
