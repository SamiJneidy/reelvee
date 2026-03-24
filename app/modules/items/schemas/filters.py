from pydantic import BaseModel

from beanie import PydanticObjectId
from app.core.enums import ItemStatus, ItemType


class ItemFilters(BaseModel):
    name: str | None = None
    category_id: PydanticObjectId | None = None
    status: ItemStatus | None = None
    visibility: bool | None = None
    slug: str | None = None
    type: ItemType | None = None
