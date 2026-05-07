from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.core.enums import ItemType
from app.shared.models.base import BaseDocument


class InvoiceCounter(Document):
    """Per-store sequential counter for invoice numbers.

    One document exists per store (keyed by the owner's user_id as ``_id``).
    Incremented atomically via ``find_one_and_update`` so concurrent invoice
    creation never produces duplicate numbers.
    """

    seq: int = 0

    class Settings:
        name = "invoice_counters"


class InvoiceCustomer(BaseModel):
    id: PydanticObjectId
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class InvoiceItem(BaseModel):
    id: PydanticObjectId
    name: str
    price: float
    quantity: int = 1
    subtotal: float
    type: ItemType


class Invoice(BaseDocument):
    user_id: PydanticObjectId
    invoice_number: str   # set by the service on create
    order_id: PydanticObjectId | None = None
    order_number: str | None = None
    customer: InvoiceCustomer
    items: list[InvoiceItem]
    subtotal: float
    discount: float = 0
    total: float
    notes: str | None = None

    class Settings:
        name = "invoices"
        indexes = [
            IndexModel(
                [("user_id", ASCENDING), ("invoice_number", ASCENDING)],
                unique=True,
                partialFilterExpression={"invoice_number": {"$type": "string"}},
            ),
            IndexModel(
                [("user_id", ASCENDING), ("order_id", ASCENDING)],
                unique=True,
                partialFilterExpression={"order_id": {"$type": "objectId"}},
            ),
            IndexModel([("user_id", ASCENDING), ("order_number", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("customer.id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("items.id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ]
