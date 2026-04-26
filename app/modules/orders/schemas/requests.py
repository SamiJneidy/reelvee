from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.core.enums import OrderStatus
from app.modules.customers.schemas.requests import CustomerCreatePublic
from app.modules.orders.schemas.base import OrderBase


class OrderItemInput(BaseModel):
    """A line item in a create or update request — ID + quantity only.
    The service resolves the item and builds the snapshot."""
    id: PydanticObjectId
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)

class OrderItemInputPublic(BaseModel):
    """A line item in a create or update request — ID + quantity only.
    The service resolves the item and builds the snapshot."""
    id: PydanticObjectId
    quantity: int = Field(1, ge=1)

class OrderCreate(OrderBase):
    customer_id: PydanticObjectId
    items: list[OrderItemInput] = Field(min_length=1)
    status: OrderStatus
    total: float | None = Field(None, ge=0)
    total_cost: float | None = Field(None, ge=0)


class OrderCreatePublic(BaseModel):
    """Used by the public storefront — customer data provided directly, not looked up."""
    customer: CustomerCreatePublic
    items: list[OrderItemInputPublic] = Field(min_length=1)
    customer_message: str | None = None


class OrderUpdate(OrderBase):
    items: list[OrderItemInputPublic] | None = None
    total: float | None = Field(None, ge=0)
    total_cost: float | None = Field(None, ge=0)
    status: OrderStatus | None = None
    is_read: bool | None = None
