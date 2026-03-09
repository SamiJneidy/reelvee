from pydantic import BaseModel

from app.core.enums import ProductStatus

from app.modules.products.models import ProductAttribute


class ProductBase(BaseModel):
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
    attributes: list[ProductAttribute] = []
