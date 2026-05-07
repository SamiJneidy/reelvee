from beanie import PydanticObjectId
from pydantic import BaseModel, Field, ConfigDict

class InvoiceItemInput(BaseModel):
    id: PydanticObjectId
    quantity: int = Field(1, ge=0)
    price: float = Field(..., ge=0)
    
    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    order_id: PydanticObjectId | None = None
    customer_id: PydanticObjectId
    items: list[InvoiceItemInput] = Field(min_length=1)
    subtotal: float
    discount: float = 0
    total: float
    notes: str | None = None


