from pydantic import BaseModel

from app.core.enums import DeliveryStatus
from app.modules.orders.models import PaymentDetails


class OrderBase(BaseModel):
    """Shared readable fields for response/internal schemas. Not used for request input."""
    discount_amount: float
    shipping_fees: float
    extra_fees: float
    payment: PaymentDetails | None
    customer_message: str | None
    address: str | None
    delivery_status: DeliveryStatus | None
    notes: str | None
