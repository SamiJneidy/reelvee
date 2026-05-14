from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Self

class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8)
    confirm_password: str = Field(..., example="abcABC123", min_length=8)
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

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
    
class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., example="refresh_token")

class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(None, example="refresh_token")
