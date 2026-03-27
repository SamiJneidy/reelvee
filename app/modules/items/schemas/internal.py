from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict

from app.core.enums import ItemStatus, ItemType
from app.modules.items.models import ItemAttribute
from app.modules.storage.schemas import FileInput

from .base import ItemBase
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin, TenantMixin

class ItemInternal(ItemBase, BaseModelWithId, TimeMixin, TenantMixin):
    slug: str
    model_config = ConfigDict(from_attributes=True)


class ItemUpdateInternal(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    cost: float | None = None
    thumbnail: FileInput | None = None
    images: list[FileInput] | None = None
    categories: list[PydanticObjectId] | None = None
    tags: list[str] | None = None
    status: ItemStatus | None = None
    is_visible: bool | None = None
    slug: str | None = None
    attributes: list[ItemAttribute] | None = None
    type: ItemType | None = None