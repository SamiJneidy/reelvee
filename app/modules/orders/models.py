from datetime import datetime

from beanie import Document, PydanticObjectId, Link
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.enums import (
    DeliveryStatus,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    RecordSource,
)
from app.modules.customers.models import Customer
from app.modules.items.models import Item
from app.shared.models.base import BaseDocument


class OrderCounter(Document):
    """Per-store sequential counter for order reference numbers.

    One document exists per store (keyed by the owner's user_id as ``_id``).
    The ``seq`` field holds the last assigned reference number; it is
    incremented atomically via ``find_one_and_update`` so concurrent order
    creation never produces duplicate numbers.
    """

    seq: int = 0

    class Settings:
        name = "order_counters"


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
    customer_id: PydanticObjectId | None = None
    item_id: PydanticObjectId
    customer: Link[Customer] | None = None
    item: Link[Item] | None = None

    # Pricing
    item_price: float | None = None     # listed price at order time, for reference
    quantity: int | None = None
    total: float | None = None          # actual revenue agreed with customer
    total_cost: float | None = None     # expense for this order

    # Payment
    payment: PaymentDetails | None = None

    # Workflow — source has no default, always set explicitly by the service
    source: RecordSource
    status: OrderStatus = OrderStatus.NEW
    is_read: bool = False

    # Reference
    reference_number: str | None = None  # per-store sequential number, set by the service on create

    # Details
    customer_message: str | None = None
    address: str | None = None
    delivery_status: DeliveryStatus | None = None
    notes: str | None = None
    
    class Settings:
        name = "orders"
        indexes = [
            IndexModel([("user_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("is_read", ASCENDING)]),
            IndexModel([("customer_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("item_id", ASCENDING)]),
            IndexModel(
                [("user_id", ASCENDING), ("reference_number", ASCENDING)],
                unique=True,
                partialFilterExpression={"reference_number": {"$type": "string"}},
            ),
        ]
