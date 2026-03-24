from fastapi import Depends
from typing import Annotated

from app.modules.items.repository import ItemRepository
from app.modules.items.service import ItemService
from app.modules.categories.dependencies import CategoryService, get_category_service
from app.modules.storage.dependencies import StorageService, get_storage_service


def get_item_repository() -> ItemRepository:
    return ItemRepository()


def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> ItemService:
    return ItemService(item_repo, storage_service, category_service)
