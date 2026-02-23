from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from app.core.enums import UserStatus, UserStep

from .base import UserBase


class UserResponse(UserBase):
    id: PydanticObjectId
    last_login: datetime | None = None
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class UserMinimal(BaseModel):
    id: PydanticObjectId
    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus
    model_config = ConfigDict(from_attributes=True)
