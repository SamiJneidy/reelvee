from typing import Annotated

from fastapi import Depends

from app.modules.categories.repository import CategoryRepository
from app.modules.categories.service import CategoryService


def get_category_repository() -> CategoryRepository:
    return CategoryRepository()


def get_category_service(
    category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    return CategoryService(category_repo)
