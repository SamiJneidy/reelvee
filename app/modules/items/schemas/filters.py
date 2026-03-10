from pydantic import BaseModel

from app.core.enums import ItemStatus


class ItemFilters(BaseModel):
    name: str | None = None
    category: str | None = None
    status: ItemStatus | None = None
    visibility: bool | None = None
    slug: str | None = None
