from pydantic import BaseModel

from app.core.enums import ItemStatus, ItemType

from app.modules.items.models import ItemAttribute


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    cost: float | None = None
    featured_img: str | None = None
    item_gallery: list[str] = []
    category: str | None = None
    tags: list[str] = []
    status: ItemStatus
    visibility: bool
    attributes: list[ItemAttribute] = []
    type: ItemType
