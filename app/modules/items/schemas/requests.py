from pydantic import BaseModel, Field

from app.core.enums import ItemStatus, ItemType
from app.modules.items.models import ItemAttribute
from app.modules.storage.schemas import FileInput, FileResponse

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name is required")
    description: str | None = Field(None, min_length=1, max_length=250, description="Item description, max 250 characters")
    price: float = Field(..., ge=1, description="Price is required")
    cost: float | None = Field(None, ge=0, description="Item cost")
    thumbnail: FileInput | None = Field(None, description="Item thumbnail")
    images: list[FileInput] = Field([], description="Item images")
    category: str | None = Field(None, min_length=1, description="Item category")
    tags: list[str] = Field([], description="Item tags")
    status: ItemStatus
    visibility: bool
    attributes: list[ItemAttribute] = Field([], description="Item attributes (name, value pairs)")
    type: ItemType = Field(..., description="Item type")


class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1, max_length=250)
    price: float | None = Field(None, ge=1)
    cost: float | None = None
    thumbnail: FileInput | None = Field(None, description="Item thumbnail")
    images: list[FileInput] | None = None
    category: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    status: ItemStatus | None = None
    visibility: bool | None = None
    attributes: list[ItemAttribute] | None = None
