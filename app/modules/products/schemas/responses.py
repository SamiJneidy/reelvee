from datetime import datetime

from pydantic import ConfigDict

from app.core.enums import ProductStatus
from app.modules.products.models import ProductAttribute
from app.shared.schemas.common import BaseModelWithId, TimeMixin

from .base import ProductBase


class ProductResponse(ProductBase, BaseModelWithId, TimeMixin):
    slug: str
    model_config = ConfigDict(from_attributes=True)

class ProductPublicResponse(BaseModelWithId):
    name: str
    slug: str
    description: str | None = None
    price: float
    featured_img: str | None = None
    product_gallery: list[str] = []
    category: str | None = None
    tags: list[str] = []
    status: ProductStatus
    attributes: list[ProductAttribute] = []

    model_config = ConfigDict(from_attributes=True)