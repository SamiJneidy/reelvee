from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.modules.users.schemas.responses import UserResponse

class SignUpResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    model_config = ConfigDict(from_attributes=True)


class VerifyEmailResponse(BaseModel):
    user: UserResponse
    sign_up_complete_token: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ResetPasswordResponse(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class RequestEmailVerificationResponse(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str | None = None
    refresh_token: str | None = None
    sign_up_complete_token: str | None = None
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)


class CurrentSessionResponse(BaseModel):
    user: UserResponse
    model_config = ConfigDict(from_attributes=True)


class SwaggerLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    model_config = ConfigDict(from_attributes=True)
