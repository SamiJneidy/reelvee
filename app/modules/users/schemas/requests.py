from pydantic import BaseModel, EmailStr, Field
from app.core.enums import UserPlan


class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
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
    links: list[str] | None = None


class UserPasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8)
