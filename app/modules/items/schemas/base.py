from beanie import PydanticObjectId
from pydantic import BaseModel

from app.core.enums import ItemStatus, ItemType

from app.modules.items.models import ItemAttribute
from app.modules.storage.schemas import FileResponse

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    cost: float | None = None
    thumbnail: FileResponse | None = None
    images: list[FileResponse] = []
    categories: list[PydanticObjectId] = []
    tags: list[str] = []
    status: ItemStatus
    is_visible: bool
    attributes: list[ItemAttribute] = []
    type: ItemType
