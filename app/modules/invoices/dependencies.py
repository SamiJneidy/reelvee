from typing import Annotated

from fastapi import Depends

from app.modules.customers.dependencies import CustomerService, get_customer_service
from app.modules.items.dependencies import ItemService, get_item_service
from app.modules.orders.dependencies import OrderService, get_order_service
from app.modules.invoices.repository import InvoiceRepository
from app.modules.invoices.service import InvoiceService


def get_invoice_repository() -> InvoiceRepository:
    return InvoiceRepository()


def get_invoice_service(
    invoice_repo: Annotated[InvoiceRepository, Depends(get_invoice_repository)],
    order_service: Annotated[OrderService, Depends(get_order_service)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> InvoiceService:
    return InvoiceService(invoice_repo, order_service, customer_service, item_service)
