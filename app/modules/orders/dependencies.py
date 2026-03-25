from typing import Annotated

from fastapi import Depends

from app.modules.orders.repository import OrderRepository
from app.modules.orders.service import OrderService


def get_order_repository() -> OrderRepository:
    return OrderRepository()


def get_order_service(
    order_repo: Annotated[OrderRepository, Depends(get_order_repository)],
) -> OrderService:
    return OrderService(order_repo)
