from beanie import PydanticObjectId
from pydantic import BaseModel

class InvoiceFilters(BaseModel):
    invoice_number: str | None = None
    order_number: str | None = None
    order_id: PydanticObjectId | None = None
    customer_id: PydanticObjectId | None = None
    item_id: PydanticObjectId | None = None
