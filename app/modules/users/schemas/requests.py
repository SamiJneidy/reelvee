from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.core.enums import UserPlan, UserStatus, UserStep
from app.modules.storage.schemas import FileInput
from app.shared.schemas.common import Link


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None
    plan: UserPlan | None = None
    status: UserStatus = UserStatus.PENDING
    step: UserStep = UserStep.ONE
    is_email_verified: bool = False
    is_completed: bool = False
    is_deleted: bool = False
    last_login: datetime | None = None
    invalid_login_attempts: int = 0


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None


class SignUpCompleteRequest(BaseModel):
    """User profile fields and initial store page setup sent together during onboarding."""
    # User fields
    first_name: str
    last_name: str
    country_code: str
    whatsapp_number: str
    address: str | None = None

    # Store fields (used to create the stores document)
    store_url: str
    logo: FileInput | None = None
    business_name: str | None = None
    business_description: str | None = None
    links: list[Link] = Field(
        default_factory=list,
        example=[{"name": "instagram", "url": "https://www.instagram.com/your_username"}],
    )


class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr = Field(..., example="newuser@example.com")
    password: str = Field(..., example="abcABC123")


class ChangeEmailRequest(BaseModel):
    token: str = Field(...)
