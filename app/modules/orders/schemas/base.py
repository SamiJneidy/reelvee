from pydantic import BaseModel

from app.core.enums import DeliveryStatus
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    """Shared readable fields for response/internal schemas. Not used for request input."""
    discount_amount: float = 0.0
    shipping_fees: float = 0.0
    extra_fees: float = 0.0
    payment: PaymentDetails | None = None
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
