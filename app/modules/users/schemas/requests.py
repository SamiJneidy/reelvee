from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.core.enums import UserPlan, UserStatus, UserStep
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
    logo: str | None = None
    business_name: str | None = None
    business_description: str | None = None
    store_url: str | None = None
    links: list[Link] = []
    qr_code: str | None = None
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
    logo: str | None = None
    business_name: str | None = None
    business_description: str | None = None
    links: list[Link] | None = None

class SignUpCompleteRequest(BaseModel):
    first_name: str
    last_name: str
    country_code: str
    whatsapp_number: str
    address: str | None = None
    logo: str | None = None
    business_name: str | None = None
    business_description: str | None = None
    store_url: str
    links: list[Link] = Field([], example=[{"name": "instagram", "url": "https://www.instagram.com/your_username"}])

class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr = Field(..., example="newuser@example.com")
    password: str = Field(..., example="abcABC123")

class ChangeEmailRequest(BaseModel):
    token: str = Field(...)