from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.modules.users.schemas.responses import UserResponse

class SignUpResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    model_config = ConfigDict(from_attributes=True)


class VerifyEmailResponse(BaseModel):
    email: EmailStr 


class ResetPasswordResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class RequestEmailVerificationResponse(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    user: UserResponse


class CurrentSessionResponse(BaseModel):
    user: UserResponse