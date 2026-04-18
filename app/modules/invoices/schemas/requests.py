from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    order_number: str | None = None
    order_reference_number: str | None = None
    customer_id: PydanticObjectId
    item_id: PydanticObjectId
    quantity: int = Field(1, ge=1)
    currency: str
    subtotal: float = Field(ge=0)
    discount: float = Field(0.0, ge=0)
    shipping_costs: float = Field(0.0, ge=0)
    total: float = Field(ge=0)
