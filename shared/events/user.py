from typing import Literal

from pydantic import BaseModel


class UserCreatedEvent(BaseModel):
    event: Literal["user_created"] = "user_created"
    user_id: str
    name: str
    email: str
