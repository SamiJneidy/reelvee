from fastapi import Depends
from typing import Annotated

from app.modules.items.repository import ItemRepository
from app.modules.items.service import ItemService


def get_item_repository() -> ItemRepository:
    return ItemRepository()


def get_item_service(
    item_repo: Annotated[ItemRepository, Depends(get_item_repository)],
) -> ItemService:
    return ItemService(item_repo)
