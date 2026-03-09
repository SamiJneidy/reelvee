import re
from typing import Any

from beanie import PydanticObjectId

from app.modules.products.models import Product


class ProductRepository:

    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("status") is not None:
            filters_list.append(Product.status == filters["status"])
        if filters.get("visibility") is not None:
            filters_list.append(Product.visibility == filters["visibility"])
        if filters.get("name"):
            filters_list.append(
                {"name": {"$regex": re.escape(filters["name"]), "$options": "i"}}
            )
        if filters.get("category"):
            filters_list.append(
                {"category": {"$regex": re.escape(filters["category"]), "$options": "i"}}
            )
        if filters.get("slug"):
            filters_list.append(
                {"slug": {"$regex": re.escape(filters["slug"]), "$options": "i"}}
            )
        return filters_list

    # -----------------------------------------------------------------
    # Public (no context scope)
    # -----------------------------------------------------------------

    async def get_by_id(self, user_id: str, id: str, session=None) -> Product | None:
        return await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.id == PydanticObjectId(id),
            session=session,
        )

    async def get_by_slug(self, user_id: str, slug: str, session=None) -> Product | None:
        return await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.slug == slug,
            session=session,
        )

    async def get_list(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Product]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Product.user_id == PydanticObjectId(user_id))
        query = Product.find(*filters_list, session=session)
        total = await query.count()
        products = await query.skip(skip).limit(limit).to_list()
        return total, products

    # -----------------------------------------------------------------
    # Owner-scoped (user_id required)
    # -----------------------------------------------------------------

    async def get_own_by_id(self, user_id: str, id: str, session=None) -> Product | None:
        return await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.id == PydanticObjectId(id),
            session=session,
        )

    async def get_own_by_slug(self, user_id: str, slug: str, session=None) -> Product | None:
        return await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.slug == slug,
            session=session,
        )

    async def count_own_by_slug(self, user_id: str, slug: str, session=None) -> int:
        return await Product.find(
            Product.user_id == PydanticObjectId(user_id),
            Product.slug == slug,
            session=session,
        ).count()

    async def get_own_list(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Product]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Product.user_id == PydanticObjectId(user_id))
        query = Product.find(*filters_list, session=session)
        total = await query.count()
        products = await query.skip(skip).limit(limit).to_list()
        return total, products

    async def create(self, data: dict[str, Any], session=None) -> Product:
        product = Product(**data)
        await product.insert(session=session)
        return product

    async def update_own_by_id(
        self, user_id: str, id: str, data: dict[str, Any], session=None
    ) -> Product | None:
        product = await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.id == PydanticObjectId(id),
            session=session,
        )
        if product is None:
            return None
        for key, value in data.items():
            if hasattr(Product, key):
                setattr(product, key, value)
        await product.save(session=session)
        return product

    async def delete_own_by_id(self, user_id: str, id: str, session=None) -> None:
        product = await Product.find_one(
            Product.user_id == PydanticObjectId(user_id),
            Product.id == PydanticObjectId(id),
            session=session,
        )
        if product is not None:
            await product.delete(session=session)
