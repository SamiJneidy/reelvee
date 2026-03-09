from pydantic import BaseModel, Field

from app.core.enums import ProductStatus

from app.modules.products.models import ProductAttribute


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name is required")
    description: str | None = Field(None, min_length=1, max_length=250, description="Product description, max 250 characters")
    price: float = Field(..., ge=1, description="Price is required")
    cost: float | None = Field(None, ge=0, description="Product cost")
    featured_img: str | None = Field(None, min_length=1, description="Product featured image")
    product_gallery: list[str] = Field([], description="Product gallery is an array of image URLs")
    category: str | None = Field(None, min_length=1, description="Product category")
    tags: list[str] = Field([], description="Product tags")
    status: ProductStatus
    visibility: bool
    attributes: list[ProductAttribute] = Field([], description="Product attributes (name, value pairs)")


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1, max_length=250)
    price: float | None = Field(None, ge=1)
    cost: float | None = None
    featured_img: str | None = Field(None, min_length=1)
    product_gallery: list[str] | None = Field(None, min_length=1)
    category: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    status: ProductStatus | None = None
    visibility: bool | None = None
    attributes: list[ProductAttribute] | None = None
