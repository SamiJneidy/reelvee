from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import ProductStatus
from app.modules.products.models import ProductAttribute

from .base import ProductBase
from app.shared.schemas.common import TimeMixin, BaseModelWithId

class ProductInternal(ProductBase, BaseModelWithId, TimeMixin):
    slug: str
    model_config = ConfigDict(from_attributes=True)


class ProductUpdateInternal(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    cost: float | None = None
    featured_img: str | None = None
    product_gallery: list[str] | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: ProductStatus | None = None
    visibility: bool | None = None
    slug: str | None = None
    attributes: list[ProductAttribute] | None = None
