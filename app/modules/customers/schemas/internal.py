from pydantic import BaseModel, ConfigDict

from app.core.enums import CustomerStatus, RecordSource
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import CustomerBase


class CustomerInternal(CustomerBase, BaseModelWithId, TimeMixin):
    model_config = ConfigDict(from_attributes=True)


class CustomerUpdateInternal(BaseModel):
    name: str | None = None
    country_code: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    notes: str | None = None
    source: RecordSource | None = None
    is_favourite: bool | None = None
    status: CustomerStatus | None = None
