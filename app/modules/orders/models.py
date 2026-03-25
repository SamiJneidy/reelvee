from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.enums import (
    DeliveryStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    RecordSource,
)
from app.shared.models.base import BaseDocument


class PaymentDetails(BaseModel):
    status: PaymentStatus
    method: PaymentMethod | None = None
    amount_paid: float | None = None
    paid_at: datetime | None = None
    reference: str | None = None
    notes: str | None = None


class Order(BaseDocument):
    # Relationships
    user_id: PydanticObjectId
    customer_id: PydanticObjectId
    item_id: PydanticObjectId

    # Pricing
    item_price: float | None = None     # listed price at order time, for reference
    quantity: int | None = None
    total: float | None = None          # actual revenue agreed with customer
    total_cost: float | None = None     # expense for this order

    # Payment
    payment: PaymentDetails

    # Workflow — source has no default, always set explicitly by the service
    source: RecordSource
    status: OrderStatus = OrderStatus.NEW
    is_read: bool = False

    # Details
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    owner_notes: str | None = None

    class Settings:
        name = "orders"
        indexes = [
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_read", ASCENDING)]),
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("item_id", ASCENDING)]),
        ]
