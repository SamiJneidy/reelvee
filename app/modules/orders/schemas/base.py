from pydantic import BaseModel

from app.core.enums import DeliveryStatus
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    discount_amount: float
    shipping_fees: float
    extra_fees: float
    total_cost: float
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
