from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Self

from app.modules.users.schemas.internal import UserInternal
from app.shared.schemas.common import Link

class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8)
    confirm_password: str = Field(..., example="abcABC123", min_length=8)
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

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
    links: list[Link] = Field(..., example=[{"name": "Instagram", "url": "https://www.instagram.com/your_username"}])

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123")

class VerifyEmailRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    code: str = Field(..., example="123456")

class RequestPasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")

class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    email: EmailStr = Field(..., example="user@example.com")
    new_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    
class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr = Field(..., example="newuser@example.com")
    password: str = Field(..., example="abcABC123")

class ChangeEmailRequest(BaseModel):
    token: str = Field(...)
