from pydantic import ConfigDict

from app.core.enums import ItemStatus, ItemType
from app.modules.categories.schemas import CategoryResponse
from app.modules.items.models import ItemAttribute
from app.modules.storage.schemas import FileResponse
from app.shared.schemas.base import BaseModelWithId
from app.shared.schemas.mixins import TimeMixin

from .base import ItemBase


class ItemResponse(ItemBase, BaseModelWithId, TimeMixin):
    slug: str
    categories: list[CategoryResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ItemPublicResponse(BaseModelWithId):
    name: str
    slug: str
    description: str | None = None
    price: float
    thumbnail: FileResponse | None = None
    images: list[FileResponse] = []
    categories: list[CategoryResponse] = []
    tags: list[str] = []
    status: ItemStatus
    attributes: list[ItemAttribute] = []
    type: ItemType

    model_config = ConfigDict(from_attributes=True)
