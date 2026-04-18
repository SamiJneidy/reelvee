from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from pymongo import ASCENDING, DESCENDING, IndexModel

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
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class InvoiceItem(BaseModel):
    name: str
    quantity: int = 1


class Invoice(BaseDocument):
    user_id: PydanticObjectId
    invoice_number: str | None = None   # set by the service on create
    order_number: str | None = None
    order_reference_number: str | None = None
    item_id: PydanticObjectId | None = None
    customer: InvoiceCustomer
    item: InvoiceItem | None = None
    currency: str
    subtotal: float
    discount: float = 0.0
    shipping_costs: float = 0.0
    total: float

    class Settings:
        name = "invoices"
        indexes = [
            IndexModel(
                [("user_id", ASCENDING), ("invoice_number", ASCENDING)],
                unique=True,
                partialFilterExpression={"invoice_number": {"$type": "string"}},
            ),
            IndexModel([("user_id", ASCENDING), ("order_number", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("order_reference_number", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("item_id", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ]
