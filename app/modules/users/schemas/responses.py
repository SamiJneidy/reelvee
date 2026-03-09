from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.enums import UserStatus, UserStep
from app.shared.schemas.common import BaseModelWithId

from .base import UserBase


class UserResponse(UserBase, BaseModelWithId):
    last_login: datetime | None = None
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class UserMinimal(BaseModel):
    id: str

    @field_validator("id", mode="before")
    @classmethod
    def id_to_str(cls, v):
        return str(v) if v is not None else v

    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus
    model_config = ConfigDict(from_attributes=True)


class SignUpCompleteResponse(BaseModel):
    user: UserResponse