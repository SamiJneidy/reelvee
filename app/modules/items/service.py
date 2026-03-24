from beanie import PydanticObjectId
from slugify import slugify

from app.core.context import CurrentUser
from app.core.enums import PermanentFileUploadPath
from app.modules.categories.schemas import CategoryResponse
from app.modules.categories.service import CategoryService
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
from app.modules.storage.schemas import FileInput, FileResponse


class ItemService:
    def __init__(
        self,
        item_repo: ItemRepository,
        storage_service: StorageService,
        category_service: CategoryService,
    ) -> None:
        self._repo = item_repo
        self._storage_service = storage_service
        self._category_service = category_service

    async def _generate_slug(self, user_id: PydanticObjectId, name: str) -> str:
        base_slug = slugify(name)
        last_slug = await self._repo.get_last_own_slug_by_base(user_id, base_slug)
        if last_slug is None:
            return base_slug
        if last_slug == base_slug:
            return f"{base_slug}-1"
        last_number = last_slug.split("-")[-1]
        return f"{base_slug}-{int(last_number) + 1}"

    async def _validate_categories(self, category_ids: list[PydanticObjectId]) -> None:
        for category_id in category_ids:
            await self._category_service.get_by_id(category_id)

    async def _resolve_categories(self, category_ids: list[PydanticObjectId]) -> list[CategoryResponse]:
        categories = []
        for cat_id in category_ids:
            cat = await self._category_service.get_by_id(cat_id)
            categories.append(CategoryResponse.model_validate(cat))
        return categories

    async def _to_item_response(self, item) -> ItemResponse:
        internal = ItemInternal.model_validate(item)
        data = internal.model_dump()
        data["categories"] = await self._resolve_categories(internal.categories)
        return ItemResponse.model_validate(data)

    async def _to_public_response(self, item) -> ItemPublicResponse:
        internal = ItemInternal.model_validate(item)
        data = internal.model_dump()
        data["categories"] = await self._resolve_categories(internal.categories)
        return ItemPublicResponse.model_validate(data)

    # -----------------------------------------------------------------
    # Public (no context scope)
    # -----------------------------------------------------------------

    async def get_by_slug(self, user_id: PydanticObjectId, slug: str) -> ItemPublicResponse:
        item = await self._repo.get_by_slug(user_id, slug)
        if not item:
            raise ItemNotFoundException()
        return await self._to_public_response(item)

    async def get_list(
        self,
        user_id: PydanticObjectId,
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
        enriched = []
        for p in items:
            enriched.append(await self._to_public_response(p))
        return total, enriched

    # -----------------------------------------------------------------
    # Owner-scoped (context required)
    # -----------------------------------------------------------------

    async def get_own_by_id(self, current_user: CurrentUser, id: PydanticObjectId) -> ItemResponse:
        item = await self._repo.get_own_by_id(current_user.user.id, id)
        if not item:
            raise ItemNotFoundException()
        return await self._to_item_response(item)

    async def get_own_by_slug(self, current_user: CurrentUser, slug: str) -> ItemResponse:
        item = await self._repo.get_own_by_slug(current_user.user.id, slug)
        if not item:
            raise ItemNotFoundException()
        return await self._to_item_response(item)

    async def get_own_list(
        self,
        current_user: CurrentUser,
        skip: int = 0,
        limit: int = 20,
        filters: ItemFilters | None = None,
    ) -> tuple[int, list[ItemResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, items = await self._repo.get_own_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        enriched = []
        for p in items:
            enriched.append(await self._to_item_response(p))
        return total, enriched

    async def create(self, current_user: CurrentUser, payload: ItemCreate, session=None) -> ItemResponse:
        data = payload.model_dump()
        data["slug"] = await self._generate_slug(current_user.user.id, payload.name)
        data["user_id"] = current_user.user.id
        await self._validate_categories(payload.categories)
        if payload.thumbnail:
            thumbnail = await self.save_thumbnail(payload.thumbnail)
            data["thumbnail"] = thumbnail.model_dump()
        if payload.images:
            images = await self.save_images(payload.images)
            data["images"] = [image.model_dump() for image in images]
        item = await self._repo.create(data, session=session)
        return await self._to_item_response(item)

    async def update_own_by_id(
        self,
        current_user: CurrentUser,
        id: PydanticObjectId,
        data: ItemUpdate | ItemUpdateInternal,
        session=None,
    ) -> ItemResponse:

        item = await self.get_own_by_id(current_user, id)
        new_images = data.images
        new_thumbnail = data.thumbnail
        new_categories = data.categories
        update_data = data.model_dump(exclude_none=True, exclude={"images"})
        if new_categories is not None:
            await self._validate_categories(new_categories)
    
        updated_item = await self._repo.update_own_by_id(current_user.user.id, id, update_data, session=session)
        
        if new_thumbnail:
            new_thumbnail = await self.save_thumbnail(new_thumbnail)
            await self.delete_thumbnail(current_user, id, session=session)
            updated_item = await self._repo.update_own_by_id(current_user.user.id, id, {"thumbnail": new_thumbnail}, session=session)

        if new_images:
            new_images = await self.save_images(new_images)
            await self.delete_deprecated_images(new_images, item.images)
            updated_item = await self._repo.update_own_by_id(current_user.user.id, id, {"images": new_images}, session=session)
        
        return await self._to_item_response(updated_item)

    async def delete_thumbnail(self, current_user: CurrentUser, id: PydanticObjectId, session=None) -> None:
        item = await self.get_own_by_id(current_user, id)
        if not item.thumbnail:
            return None
        await self._storage_service.delete_file(item.thumbnail.key)
        await self._repo.update_own_by_id(current_user.user.id, id, {"thumbnail": None}, session=session)

    async def delete_own_by_id(self, current_user: CurrentUser, id: PydanticObjectId, session=None) -> None:
        item = await self._repo.get_own_by_id(current_user.user.id, id, session=session)
        if not item:
            raise ItemNotFoundException()
        await self._repo.delete_own_by_id(current_user.user.id, id, session=session)
    
    async def save_thumbnail(self, file: FileInput) -> FileResponse:
        if file.url:
            return FileResponse.model_validate(file)
        data = await self._storage_service.finalize_file(
            file=file,
            destination_path=PermanentFileUploadPath.ITEM_THUMBNAIL.value
        )
        return FileResponse.model_validate(data)

    async def save_images(self, images: list[FileInput]) -> list[FileResponse]:
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