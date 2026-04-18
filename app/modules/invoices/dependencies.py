from typing import Annotated

from fastapi import Depends

from app.modules.customers.dependencies import CustomerService, get_customer_service
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.service import InvoiceService
from app.modules.items.dependencies import ItemService, get_item_service


def get_invoice_repository() -> InvoiceRepository:
    return InvoiceRepository()


def get_invoice_service(
    invoice_repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
) -> InvoiceService:
    return InvoiceService(invoice_repo, item_service, customer_service)
