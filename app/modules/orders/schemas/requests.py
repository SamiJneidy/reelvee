from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.core.enums import DeliveryStatus, OrderStatus
from app.modules.customers.schemas.requests import CustomerCreatePublic
from app.modules.orders.models import PaymentDetails


class OrderItemInput(BaseModel):
    """Line item for internal create/update — price can be overridden by the owner."""
    id: PydanticObjectId
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)


class OrderItemInputPublic(BaseModel):
    """Line item for the public storefront — price is always taken from the catalogue."""
    id: PydanticObjectId
    quantity: int = Field(1, ge=1)


class OrderCreate(BaseModel):
    customer_id: PydanticObjectId
    items: list[OrderItemInput] = Field(min_length=1)
    status: OrderStatus
    discount_amount: float = Field(0.0, ge=0)
    shipping_fees: float = Field(0.0, ge=0)
    extra_fees: float = Field(0.0, ge=0)
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None


class OrderCreatePublic(BaseModel):
    """Used by the public storefront — customer data provided inline, not looked up."""
    customer: CustomerCreatePublic
    items: list[OrderItemInputPublic] = Field(min_length=1)
    customer_message: str | None = None


class OrderUpdate(BaseModel):
    """PATCH schema — every field is optional; only sent fields are applied."""
    items: list[OrderItemInput] | None = Field(None, min_length=1)
    status: OrderStatus | None = None
    is_read: bool | None = None
    discount_amount: float | None = Field(None, ge=0)
    shipping_fees: float | None = Field(None, ge=0)
    extra_fees: float | None = Field(None, ge=0)
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
