from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ItemStatus, ItemType
from app.modules.items.models import ItemAttribute

from .base import ItemBase
from app.shared.schemas.common import TimeMixin, BaseModelWithId

class ItemInternal(ItemBase, BaseModelWithId, TimeMixin):
    slug: str
    model_config = ConfigDict(from_attributes=True)


class ItemUpdateInternal(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    cost: float | None = None
    featured_img: str | None = None
    item_gallery: list[str] | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: ItemStatus | None = None
    visibility: bool | None = None
    slug: str | None = None
    attributes: list[ItemAttribute] | None = None
    type: ItemType | None = None