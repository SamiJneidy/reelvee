from datetime import datetime

from beanie import PydanticObjectId
from pydantic import ConfigDict

from app.core.enums import UserStatus, UserStep

from .base import UserBase


class UserInternal(UserBase):
    id: PydanticObjectId
    email: str
    last_login: datetime | None = None
    invalid_login_attempts: int = 0
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    qr_code: str | None = None
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserInternal):
    password: str
