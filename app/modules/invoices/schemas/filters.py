from pydantic import BaseModel


class InvoiceFilters(BaseModel):
    invoice_number: str | None = None
    order_number: str | None = None
    order_reference_number: str | None = None
    currency: str | None = None
