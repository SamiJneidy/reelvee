from pydantic import BaseModel

from app.core.enums import CustomerStatus, RecordSource


class CustomerFilters(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    is_favourite: bool | None = None
    status: CustomerStatus | None = None
    source: RecordSource | None = None
