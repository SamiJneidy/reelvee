from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin


class InvoiceCustomerResponse(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    model_config = ConfigDict(from_attributes=True)


class InvoiceItemResponse(BaseModel):
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(BaseModelWithId, TimeMixin):
    invoice_number: str | None = None
    order_number: str | None = None
    order_reference_number: str | None = None
    customer: InvoiceCustomerResponse
    item: InvoiceItemResponse | None = None
    currency: str
    subtotal: float = Field(ge=0)
    discount: float = Field(0.0, ge=0)
    shipping_costs: float = Field(0.0, ge=0)
    total: float = Field(ge=0)
    model_config = ConfigDict(from_attributes=True)
