from typing import Self
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

class SignUpResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    model_config = ConfigDict(from_attributes=True)

class SignUpCompleteResponse(BaseModel):
    pass

class LoginResponse(BaseModel):
    user: UserOut

class VerifyEmailResponse(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(...)
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    confirm_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match")
        return self

class ResetPasswordResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
