from beanie import PydanticObjectId
from pydantic import BaseModel

from app.core.enums import DeliveryStatus, OrderStatus, RecordSource
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    customer_id: PydanticObjectId
    item_id: PydanticObjectId
    item_price: float | None = None
    quantity: float | None = None
    total: float | None = None
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
