from typing import Any
from slugify import slugify



from app.core.context import RequestContext
from app.core.enums import PermanentFileUploadPath, TempFileUploadPath
from app.modules.storage import StorageService
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
from app.modules.storage.schemas import FileInput, FileResponse, PresignedURLRequest, PresignedURLResponse


class ItemService:
    def __init__(self, item_repo: ItemRepository, storage_service: StorageService) -> None:
        self._repo = item_repo
        self._storage_service = storage_service

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
        if payload.thumbnail:
            thumbnail = await self.upload_thumbnail(payload.thumbnail)
            data["thumbnail"] = thumbnail.model_dump()
        if payload.images:
            images = await self.upload_images(payload.images)
            data["images"] = [image.model_dump() for image in images]
        item = await self._repo.create(data, session=session)
        return ItemInternal.model_validate(item)

    async def update_own_by_id(
        self,
        ctx: RequestContext,
        id: str,
        data: ItemUpdate | ItemUpdateInternal,
        session=None,
    ) -> ItemInternal:

        item = await self.get_own_by_id(ctx, id)
        new_images = data.images
        new_thumbnail = data.thumbnail
        update_data = data.model_dump(exclude_none=True, exclude={"images"})
    
        updated_item = await self._repo.update_own_by_id(ctx.user.id, id, update_data, session=session)
        
        if new_thumbnail:
            new_thumbnail = await self.upload_thumbnail(new_thumbnail)
            await self.delete_thumbnail(ctx, id, session=session)
            updated_item = await self._repo.update_own_by_id(ctx.user.id, id, {"thumbnail": new_thumbnail}, session=session)

        if new_images:
            new_images = await self.upload_images(new_images)
            await self.delete_deprecated_images(new_images, item.images)
            updated_item = await self._repo.update_own_by_id(ctx.user.id, id, {"images": new_images}, session=session)
        
        return ItemInternal.model_validate(updated_item)

    async def delete_thumbnail(self, ctx: RequestContext, id: str, session=None) -> None:
        item = await self.get_own_by_id(ctx, id)
        if not item.thumbnail:
            return None
        await self._storage_service.delete_file(item.thumbnail.key)
        await self._repo.update_own_by_id(ctx.user.id, id, {"thumbnail": None}, session=session)

    async def delete_own_by_id(self, ctx: RequestContext, id: str, session=None) -> None:
        item = await self._repo.get_own_by_id(ctx.user.id, id, session=session)
        if not item:
            raise ItemNotFoundException()
        await self._repo.delete_own_by_id(ctx.user.id, id, session=session)
    
    async def upload_thumbnail(self, file: FileInput) -> FileResponse:
        if file.url:
            return FileResponse.model_validate(file)
        data = await self._storage_service.finalize_file(
            file=file,
            destination_path=PermanentFileUploadPath.ITEM_THUMBNAIL.value
        )
        return FileResponse.model_validate(data)

    async def upload_images(self, images: list[FileInput]) -> list[FileResponse]:
        new_images = []
        for image in images:
            if image.url:
                new_images.append(FileResponse.model_validate(image))
            else:
                new_image = await self._storage_service.finalize_file(image, PermanentFileUploadPath.ITEM_IMAGE.value)
                new_images.append(FileResponse.model_validate(new_image))
        return new_images

    async def delete_deprecated_images(self, new_images: list[FileInput], old_images: list[FileResponse]) -> None:
        for image in old_images:
            if not any(new_image.key == image.key for new_image in new_images):
                await self._storage_service.delete_file(image.key)