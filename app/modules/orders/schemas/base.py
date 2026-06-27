from pydantic import BaseModel

from app.core.enums import DeliveryStatus
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    discount_amount: float = 0.0
    shipping_fees: float = 0.0
    extra_fees: float = 0.0
    total_cost: float | None = None
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
