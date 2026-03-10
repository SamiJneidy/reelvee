from typing import Any
from slugify import slugify

from beanie import PydanticObjectId

from app.core.context import RequestContext

from app.modules.items.exceptions import ItemNotFoundException
from app.modules.items.repository import ItemRepository
from app.modules.items.schemas import (
    ItemCreate,
    ItemFilters,
    ItemInternal,
    ItemUpdate,
    ItemUpdateInternal,
)
from app.modules.items.schemas.responses import ItemPublicResponse, ItemResponse


class ItemService:
    def __init__(self, item_repo: ItemRepository) -> None:
        self._repo = item_repo

    async def _generate_slug(self, user_id: str, name: str) -> str:
        slug = slugify(name)
        counter = await self._repo.count_own_by_slug(user_id, slug)
        if counter == 0:
            return slug
        return slug + "-" + str(counter)

    # -----------------------------------------------------------------
    # Public (no context scope)
    # -----------------------------------------------------------------

    async def get_by_slug(self, user_id: str, slug: str) -> ItemInternal:
        item = await self._repo.get_by_slug(user_id, slug)
        if not item:
            raise ItemNotFoundException()
        return ItemInternal.model_validate(item)

    async def get_list(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        filters: ItemFilters | None = None,
    ) -> tuple[int, list[ItemPublicResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, items = await self._repo.get_list(
            user_id=user_id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [ItemPublicResponse.model_validate(p) for p in items]

    # -----------------------------------------------------------------
    # Owner-scoped (context required)
    # -----------------------------------------------------------------

    async def get_own_by_id(self, ctx: RequestContext, id: str) -> ItemInternal:
        item = await self._repo.get_own_by_id(ctx.user.id, id)
        if not item:
            raise ItemNotFoundException()
        return ItemInternal.model_validate(item)

    async def get_own_by_slug(self, ctx: RequestContext, slug: str) -> ItemInternal:
        item = await self._repo.get_own_by_slug(ctx.user.id, slug)
        if not item:
            raise ItemNotFoundException()
        return ItemInternal.model_validate(item)

    async def get_own_list(
        self,
        ctx: RequestContext,
        skip: int = 0,
        limit: int = 20,
        filters: ItemFilters | None = None,
    ) -> tuple[int, list[ItemResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, items = await self._repo.get_own_list(
            user_id=ctx.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [ItemResponse.model_validate(p) for p in items]

    async def create(self, ctx: RequestContext, payload: ItemCreate, session=None) -> ItemInternal:
        data = payload.model_dump()
        data["slug"] = await self._generate_slug(ctx.user.id, payload.name)
        data["user_id"] = ctx.user.id
        item = await self._repo.create(data, session=session)
        return ItemInternal.model_validate(item)

    async def update_own_by_id(
        self,
        ctx: RequestContext,
        id: str,
        update_data: ItemUpdate | ItemUpdateInternal | dict[str, Any],
        session=None,
    ) -> ItemInternal:
        if isinstance(update_data, (ItemUpdate, ItemUpdateInternal)):
            update_data = update_data.model_dump(exclude_none=True)
        item = await self._repo.update_own_by_id(ctx.user.id, id, update_data, session=session)
        if not item:
            raise ItemNotFoundException()
        return ItemInternal.model_validate(item)

    async def delete_own_by_id(self, ctx: RequestContext, id: str, session=None) -> None:
        item = await self._repo.get_own_by_id(ctx.user.id, id, session=session)
        if not item:
            raise ItemNotFoundException()
        await self._repo.delete_own_by_id(ctx.user.id, id, session=session)
