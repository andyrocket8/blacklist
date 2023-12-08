from pydantic import BaseModel


class AddResponseSchema(BaseModel):
    added: int


class DeleteResponseSchema(BaseModel):
    deleted: int


class CountResponseSchema(BaseModel):
    count: int
