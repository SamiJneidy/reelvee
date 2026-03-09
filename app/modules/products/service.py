from datetime import datetime, timezone
from typing import Any
from slugify import slugify

from beanie import PydanticObjectId

from app.core.context import RequestContext

from app.modules.products.exceptions import ProductNotFoundException
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreate,
    ProductFilters,
    ProductInternal,
    ProductUpdate,
    ProductUpdateInternal,
)
from app.modules.products.schemas.responses import ProductPublicResponse, ProductResponse


class ProductService:
    def __init__(self, product_repo: ProductRepository) -> None:
        self._repo = product_repo

    async def _generate_slug(self, user_id: str, name: str) -> str:
        slug = slugify(name)
        counter = await self._repo.count_own_by_slug(user_id, slug)
        if counter == 0:
            return slug
        return slug + "-" + str(counter)

    # -----------------------------------------------------------------
    # Public (no context scope)
    # -----------------------------------------------------------------

    async def get_by_slug(self, user_id: str, slug: str) -> ProductInternal:
        product = await self._repo.get_by_slug(user_id, slug)
        if not product:
            raise ProductNotFoundException()
        return ProductInternal.model_validate(product)

    async def get_list(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        filters: ProductFilters | None = None,
    ) -> tuple[int, list[ProductPublicResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, products = await self._repo.get_list(
            user_id=user_id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [ProductPublicResponse.model_validate(p) for p in products]

    # -----------------------------------------------------------------
    # Owner-scoped (context required)
    # -----------------------------------------------------------------

    async def get_own_by_id(self, ctx: RequestContext, id: str) -> ProductInternal:
        product = await self._repo.get_own_by_id(ctx.user.id, id)
        if not product:
            raise ProductNotFoundException()
        return ProductInternal.model_validate(product)

    async def get_own_by_slug(self, ctx: RequestContext, slug: str) -> ProductInternal:
        product = await self._repo.get_own_by_slug(ctx.user.id, slug)
        if not product:
            raise ProductNotFoundException()
        return ProductInternal.model_validate(product)

    async def get_own_list(
        self,
        ctx: RequestContext,
        skip: int = 0,
        limit: int = 20,
        filters: ProductFilters | None = None,
    ) -> tuple[int, list[ProductResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, products = await self._repo.get_own_list(
            user_id=ctx.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [ProductResponse.model_validate(p) for p in products]

    async def create(self, ctx: RequestContext, payload: ProductCreate, session=None) -> ProductInternal:
        data = payload.model_dump()
        data["slug"] = await self._generate_slug(ctx.user.id, payload.name)
        data["user_id"] = ctx.user.id
        product = await self._repo.create(data, session=session)
        return ProductInternal.model_validate(product)

    async def update_own_by_id(
        self,
        ctx: RequestContext,
        id: str,
        update_data: ProductUpdate | ProductUpdateInternal | dict[str, Any],
        session=None,
    ) -> ProductInternal:
        if isinstance(update_data, (ProductUpdate, ProductUpdateInternal)):
            update_data = update_data.model_dump(exclude_none=True)
        product = await self._repo.update_own_by_id(ctx.user.id, id, update_data, session=session)
        if not product:
            raise ProductNotFoundException()
        return ProductInternal.model_validate(product)

    async def delete_own_by_id(self, ctx: RequestContext, id: str, session=None) -> None:
        product = await self._repo.get_own_by_id(ctx.user.id, id, session=session)
        if not product:
            raise ProductNotFoundException()
        await self._repo.delete_own_by_id(ctx.user.id, id, session=session)
