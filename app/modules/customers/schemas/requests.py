from pydantic import BaseModel, Field

from app.core.enums import CustomerStatus


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str | None = Field(None)
    address: str | None = Field(None)
    notes: str | None = Field(None)
    is_favourite: bool = Field(False)


class CustomerCreatePublic(BaseModel):
    name: str = Field(..., min_length=1)
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str | None = Field(None)
    address: str | None = Field(None)


class CustomerUpdate(BaseModel):
    name: str = Field(None, min_length=1)
    country_code: str = Field(None, min_length=1)
    phone: str = Field(None, min_length=1)
    is_favourite: bool = Field(None)
    status: CustomerStatus = Field(None)
    email: str | None = Field(None)
    address: str | None = Field(None)
    notes: str | None = Field(None)
