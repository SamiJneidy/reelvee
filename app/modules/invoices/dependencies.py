from typing import Annotated

from fastapi import Depends

from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.service import InvoiceService


def get_invoice_repository() -> InvoiceRepository:
    return InvoiceRepository()


def get_invoice_service(
    invoice_repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
) -> InvoiceService:
    return InvoiceService(invoice_repo)
