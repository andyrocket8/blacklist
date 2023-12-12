from pydantic import BaseModel


class AuthCheckResult(BaseModel):
    is_admin: bool
    is_authenticated_user: bool
