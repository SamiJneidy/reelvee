from beanie import PydanticObjectId
from pydantic import BaseModel

from app.modules.invoices.models import InvoiceCustomer


class InvoiceCreate(BaseModel):
    order_id: PydanticObjectId
    order_number: str | None = None
    customer: InvoiceCustomer
