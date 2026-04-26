from pydantic import BaseModel

from app.core.enums import DeliveryStatus
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    total: float | None = None
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
