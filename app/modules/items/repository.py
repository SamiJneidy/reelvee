import re
from typing import Any

from beanie import PydanticObjectId

from app.modules.items.models import Item


class ItemRepository:

    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("status") is not None:
            filters_list.append(Item.status == filters["status"])
        if filters.get("type") is not None:
            filters_list.append(Item.type == filters["type"])
        if filters.get("is_visible") is not None:
            filters_list.append(Item.is_visible == filters["is_visible"])
        if filters.get("name"):
            filters_list.append(
                {"name": {"$regex": re.escape(filters["name"]), "$options": "i"}}
            )
        if filters.get("category_id"):
            filters_list.append(
                {"categories": filters["category_id"]}
            )
        if filters.get("slug"):
            filters_list.append(
                {"slug": {"$regex": re.escape(filters["slug"]), "$options": "i"}}
            )
        return filters_list

    # -----------------------------------------------------------------
    # Public (no context scope)
    # -----------------------------------------------------------------

    async def get_by_id(self, user_id: PydanticObjectId, id: PydanticObjectId, session=None) -> Item | None:
        return await Item.find_one(
            Item.user_id == user_id,
            Item.id == id,
            session=session,
        )

    async def get_by_slug(self, user_id: PydanticObjectId, slug: str, session=None) -> Item | None:
        return await Item.find_one(
            Item.user_id == user_id,
            Item.slug == slug,
            session=session,
        )

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Item]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Item.user_id == user_id)
        query = Item.find(*filters_list, session=session)
        total = await query.count()
        items = await query.skip(skip).limit(limit).to_list()
        return total, items

    # -----------------------------------------------------------------
    # Owner-scoped (user_id required)
    # -----------------------------------------------------------------

    async def get_own_by_id(self, user_id: PydanticObjectId, id: PydanticObjectId, session=None) -> Item | None:
        return await Item.find_one(
            Item.user_id == user_id,
            Item.id == id,
            session=session,
        )

    async def get_own_by_slug(self, user_id: PydanticObjectId, slug: str, session=None) -> Item | None:
        return await Item.find_one(
            Item.user_id == user_id,
            Item.slug == slug,
            session=session,
        )

    async def get_last_own_slug_by_base(self, user_id: PydanticObjectId, base_slug: str, session=None) -> str | None:
        pattern = f"^{re.escape(base_slug)}(-\\d+)?$"
        item = await Item.find(
            Item.user_id == user_id,
            {"slug": {"$regex": pattern}},
            session=session,
        ).sort(-Item.id).limit(1).first_or_none()
        return item.slug if item else None

    async def get_own_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Item]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Item.user_id == user_id)
        query = Item.find(*filters_list, session=session)
        total = await query.count()
        items = await query.skip(skip).limit(limit).to_list()
        return total, items

    async def create(self, data: dict[str, Any], session=None) -> Item:
        item = Item(**data)
        await item.insert(session=session)
        return item

    async def update_own_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, data: dict[str, Any], session=None
    ) -> Item | None:
        item = await Item.find_one(
            Item.user_id == user_id,
            Item.id == id,
            session=session,
        )
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(Item, key):
                setattr(item, key, value)
        await item.save(session=session)
        return item

    async def delete_own_by_id(self, user_id: PydanticObjectId, id: PydanticObjectId, session=None) -> None:
        item = await Item.find_one(
            Item.user_id == user_id,
            Item.id == id,
            session=session,
        )
        if item is not None:
            await item.delete(session=session)
