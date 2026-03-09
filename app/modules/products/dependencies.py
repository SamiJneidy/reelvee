from fastapi import Depends
from typing import Annotated

from app.modules.products.repository import ProductRepository
from app.modules.products.service import ProductService


def get_product_repository() -> ProductRepository:
    return ProductRepository()


def get_product_service(
    product_repo: Annotated[ProductRepository, Depends(get_product_repository)],
) -> ProductService:
    return ProductService(product_repo)
