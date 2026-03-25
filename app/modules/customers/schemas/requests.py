from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str | None = None
    address: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    country_code: str | None = Field(None, min_length=1)
    phone: str | None = Field(None, min_length=1)
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    is_favourite: bool | None = None
    status: str | None = None
