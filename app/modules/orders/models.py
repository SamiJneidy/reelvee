from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.enums import (
    DeliveryStatus,
    ItemType,
    OrderStatus,
    RecordSource,
)
from app.modules.storage.models import File
from app.shared.models.base import BaseDocument
from app.shared.schemas.payment import PaymentDetails

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


class OrderCustomer(BaseModel):
    id: PydanticObjectId
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class OrderItem(BaseModel):
    id: PydanticObjectId
    name: str
    price: float
    quantity: int = 1
    subtotal: float
    type: ItemType
    thumbnail: File | None = None


class Order(BaseDocument):
    # Relationships
    user_id: PydanticObjectId
    customer: OrderCustomer

    # Pricing
    items: list[OrderItem] = []
    total: float | None = None          # actual revenue agreed with customer
    total_cost: float | None = None     # expense for this order

    # Payment
    payment: PaymentDetails | None = None

    # Workflow — source has no default, always set explicitly by the service
    source: RecordSource
    status: OrderStatus = OrderStatus.NEW
    is_read: bool = False

    # Reference
    order_number: str | None = None  # per-store sequential number, set by the service on create

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
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("payment.status", ASCENDING)]),
            IndexModel([("customer.id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("items.id", ASCENDING)]),
            IndexModel(
                [("user_id", ASCENDING), ("order_number", ASCENDING)],
                unique=True,
                partialFilterExpression={"order_number": {"$type": "string"}},
            ),
        ]
