from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import UserStatus, UserStep
from app.shared.schemas.base import BaseModelWithId
from app.modules.storage.schemas import FileResponse
from .base import UserBase


class UserResponse(UserBase, BaseModelWithId):
    qr_code: FileResponse | None = None
    last_login: datetime | None = None
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)


class UserMinimal(BaseModelWithId):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: UserStatus
    model_config = ConfigDict(from_attributes=True)


class SignUpCompleteResponse(BaseModel):
    user: UserResponse