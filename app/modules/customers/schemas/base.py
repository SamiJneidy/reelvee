from pydantic import BaseModel

from app.core.enums import CustomerStatus, RecordSource


class CustomerBase(BaseModel):
    name: str
    country_code: str
    phone: str
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    source: RecordSource
    status: CustomerStatus
