from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.modules.invoices.models import InvoiceCustomer, InvoiceItem


class InvoiceCreate(BaseModel):
    order_number: str | None = None
    order_reference_number: str | None = None
    item_id: PydanticObjectId | None = None
    customer: InvoiceCustomer
    item: InvoiceItem | None = None
    currency: str
    subtotal: float = Field(ge=0)
    discount: float = Field(0.0, ge=0)
    shipping_costs: float = Field(0.0, ge=0)
    total: float = Field(ge=0)
