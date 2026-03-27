from pydantic import BaseModel, EmailStr, Field

from app.core.enums import CustomerStatus


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    is_favourite: bool = False

class CustomerCreatePublic(BaseModel):
    name: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str | None = None
    address: str | None = None

class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    country_code: str | None = Field(None, min_length=1)
    phone: str | None = Field(None, min_length=1)
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    is_favourite: bool | None = None
    status: CustomerStatus | None = None
