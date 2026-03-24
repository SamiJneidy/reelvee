from pydantic import BaseModel
from beanie import Document, Indexed, Link, PydanticObjectId

from app.core.enums import ItemStatus, ItemType
from app.modules.users.models import User
from app.shared.models import BaseDocument
from app.modules.storage.models import File

class ItemAttribute(BaseModel):
    name: str
    value: str

class Item(BaseDocument):
    name: str
    description: str | None = None
    price: float
    cost: float | None = None
    thumbnail: File | None = None
    images: list[File] = []
    categories: list[PydanticObjectId] = []
    tags: list[str] = []
    status: ItemStatus
    visibility: bool
    slug: Indexed(str, unique=True)
    attributes: list[ItemAttribute] = []
    user_id: PydanticObjectId
    user: Link[User] | None = None
    type: ItemType

    class Settings:
        name = "items"
