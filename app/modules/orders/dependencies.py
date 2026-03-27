from typing import Annotated

from fastapi import Depends

from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService
from app.modules.customers.dependencies import CustomerService, get_customer_service
from app.modules.items.dependencies import ItemService, get_item_service

def get_order_repository() -> OrderRepository:
    return OrderRepository()


def get_order_service(
    order_repo: Annotated[OrderRepository, Depends(get_order_repository)],
    customer_service: Annotated[CustomerService, Depends(get_customer_service)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> OrderService:
    return OrderService(order_repo, customer_service, item_service)
