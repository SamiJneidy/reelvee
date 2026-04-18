from pydantic import BaseModel, ConfigDict, Field
from beanie import PydanticObjectId

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
    quantity: int = 1
    model_config = ConfigDict(from_attributes=True)

class InvoiceResponse(BaseModelWithId, TimeMixin):
    order_number: str | None = None
    order_reference_number: str | None = None
    item_id: PydanticObjectId | None = None
    customer: InvoiceCustomerResponse
    item: InvoiceItemResponse
    currency: str
    subtotal: float = Field(ge=0)
    discount: float = Field(0.0, ge=0)
    shipping_costs: float = Field(0.0, ge=0)
    total: float = Field(ge=0)
    invoice_number: str | None = None
    model_config = ConfigDict(from_attributes=True)
