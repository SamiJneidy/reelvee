from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import UserPlan, UserStatus, UserStep
from app.shared.schemas.base import BaseModelWithId
from .base import UserBase


class UserInternal(UserBase, BaseModelWithId):
    last_login: datetime | None = None
    invalid_login_attempts: int = 0
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserInternal):
    password: str


class UserUpdateInternal(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None
    plan: UserPlan | None = None
    status: UserStatus | None = None
    step: UserStep | None = None
    is_email_verified: bool | None = None
    is_completed: bool | None = None
    is_deleted: bool | None = None
    last_login: datetime | None = None
    invalid_login_attempts: int | None = None
