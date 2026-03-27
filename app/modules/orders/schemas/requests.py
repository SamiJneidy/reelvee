from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from app.core.enums import DeliveryStatus, OrderStatus
from app.modules.orders.models import PaymentDetails
from app.modules.customers.schemas.requests import CustomerCreatePublic


class OrderCreate(BaseModel):
    customer_id: PydanticObjectId
    item_id: PydanticObjectId
    status: OrderStatus
    item_price: float | None = Field(None, ge=0)
    quantity: float | None = Field(None, ge=1)
    total: float | None = Field(None, ge=0)
    total_cost: float | None = Field(None, ge=0)
    customer_message: str | None = None
    address: str | None = None
    notes: str | None = None
    payment: PaymentDetails | None = None
    delivery_status: DeliveryStatus | None = None

class OrderCreatePublic(BaseModel):
    customer: CustomerCreatePublic
    item_id: PydanticObjectId
    quantity: float | None = Field(None, ge=1)
    customer_message: str | None = None

class OrderUpdate(BaseModel):
    item_id: PydanticObjectId | None = None
    item_price: float | None = Field(None, ge=0)
    quantity: float | None = Field(None, ge=1)
    total: float | None = Field(None, ge=0)
    total_cost: float | None = Field(None, ge=0)
    payment: PaymentDetails | None = None
    status: OrderStatus | None = None
    is_read: bool | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
