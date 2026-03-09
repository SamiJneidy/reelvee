from datetime import datetime

from pydantic import BaseModel
from beanie import Document, Indexed, Link, PydanticObjectId

from app.core.enums import ProductStatus
from app.modules.users.models import User
from app.shared.models.mixins import BaseDocument


class ProductAttribute(BaseModel):
    name: str
    value: str


class Product(BaseDocument):
    name: str
    description: str | None = None
    price: float
    cost: float | None = None
    featured_img: str | None = None
    product_gallery: list[str] = []
    category: str | None = None
    tags: list[str] = []
    status: ProductStatus
    visibility: bool
    slug: Indexed(str, unique=True)
    attributes: list[ProductAttribute] = []
    user_id: PydanticObjectId
    user: Link[User] | None = None
    
    class Settings:
        name = "products"
