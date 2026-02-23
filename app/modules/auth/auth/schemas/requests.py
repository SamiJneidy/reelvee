from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Self

class SignUpRequest(BaseModel):
    name: str = Field(..., example="Sami")
    phone: Optional[str] = Field(None)
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    confirm_password: str = Field(..., example="abcABC123", min_length=8, description="The password must be a minimum of 8 characters in length, containing both uppercase and lowercase English letters and at least one numeric digit.")
    
    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class SignUpCompleteRequest(BaseModel):
    pass

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="abcABC123")

class SendEmailVerificationOTPRequest(BaseModel):
    email: EmailStr

class SendPasswordResetOTPRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
