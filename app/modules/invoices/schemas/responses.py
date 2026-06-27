from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin


class InvoiceCustomerResponse(BaseModel):
    id: PydanticObjectId
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    model_config = ConfigDict(from_attributes=True)


class InvoiceResponse(BaseModelWithId, TimeMixin):
    invoice_number: str
    order_id: PydanticObjectId
    order_number: str | None = None
    customer: InvoiceCustomerResponse
    pdf_url: str | None = None
    model_config = ConfigDict(from_attributes=True)


class InvoicePdfResponse(BaseModel):
    url: str
    model_config = ConfigDict(from_attributes=True)
