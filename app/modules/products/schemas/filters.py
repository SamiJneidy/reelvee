from pydantic import BaseModel

from app.core.enums import ProductStatus


class ProductFilters(BaseModel):
    name: str | None = None
    category: str | None = None
    status: ProductStatus | None = None
    visibility: bool | None = None
    slug: str | None = None
