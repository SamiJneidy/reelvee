from typing import Annotated

from fastapi import Depends

from app.modules.customers.repository import CustomerRepository
from app.modules.customers.service import CustomerService


def get_customer_repository() -> CustomerRepository:
    return CustomerRepository()


def get_customer_service(
    customer_repo: Annotated[CustomerRepository, Depends(get_customer_repository)],
) -> CustomerService:
    return CustomerService(customer_repo)
