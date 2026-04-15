from beanie import PydanticObjectId
from slugify import slugify

from app.core.context import SessionContext
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
from app.modules.storage.exceptions import FileDeleteException, FileFinalizeException, FileReplaceException
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

    async def get_by_id(self, user_id: PydanticObjectId, id: PydanticObjectId) -> ItemResponse:
        item = await self._repo.get_by_id(user_id, id)
        if not item:
            raise ItemNotFoundException()
        return await self._to_item_response(item)


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

    async def get_own_by_id(self, current_user: SessionContext, id: PydanticObjectId, session=None) -> ItemResponse:
        item = await self._repo.get_own_by_id(current_user.user.id, id, session)
        if not item:
            raise ItemNotFoundException()
        return await self._to_item_response(item)


    async def get_own_by_slug(self, current_user: SessionContext, slug: str, session=None) -> ItemResponse:
        item = await self._repo.get_own_by_slug(current_user.user.id, slug, session=session)
        if not item:
            raise ItemNotFoundException()
        return await self._to_item_response(item)


    async def get_own_list(
        self,
        current_user: SessionContext,
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


    async def create(self, current_user: SessionContext, payload: ItemCreate, session=None) -> ItemResponse:
        data = payload.model_dump(exclude={"thumbnail", "images"})
        data["slug"] = await self._generate_slug(current_user.user.id, payload.name)
        data["user_id"] = current_user.user.id
        await self._validate_categories(payload.categories)

        item = await self._repo.create(data, session=session)

        await self._update_thumbnail(
            user_id=current_user.user.id, 
            item_id=item.id, 
            new_thumbnail=payload.thumbnail, 
            session=session
        )

        await self._update_images(
            user_id=current_user.user.id, 
            item_id=item.id, 
            new_images=payload.images, 
            old_images=[],
            session=session
        )
        return await self.get_own_by_id(current_user, item.id, session)

    async def update_own_by_id(
        self,
        current_user: SessionContext,
        id: PydanticObjectId,
        data: ItemUpdate | ItemUpdateInternal,
        session=None,
    ) -> ItemResponse:

        item = await self.get_own_by_id(current_user, id)
        update_data = data.model_dump(exclude_unset=True, exclude={"images", "thumbnail"})
        
        if "categories" in data.model_fields_set:
            await self._validate_categories(data.categories)
    
        # Update first, if success then update images (thumbnail and images)
        updated_item = await self._repo.update_own_by_id(current_user.user.id, id, update_data, session=session)
        
        if "thumbnail" in data.model_fields_set:
            await self._update_thumbnail(
                user_id=current_user.user.id, 
                item_id=id, 
                new_thumbnail=data.thumbnail, 
                old_thumbnail=item.thumbnail, 
                session=session
            )

        if "images" in data.model_fields_set:
            await self._update_images(
                user_id=current_user.user.id, 
                item_id=id, 
                new_images=data.images, 
                old_images=item.images, 
                session=session
            )
        
        return await self.get_own_by_id(current_user, id, session)


    async def delete_own_by_id(self, current_user: SessionContext, id: PydanticObjectId, session=None) -> None:
        item = await self._repo.get_own_by_id(current_user.user.id, id, session=session)
        if not item:
            raise ItemNotFoundException()
        
        if item.thumbnail is not None:
            try:
                await self._storage_service.delete_file(item.thumbnail.key)
            except FileDeleteException:
                pass
        
        for image in item.images:
            try:
                await self._storage_service.delete_file(image.key)
            except FileDeleteException:
                pass
        
        await self._repo.delete_own_by_id(current_user.user.id, id, session=session)
    

    async def _update_thumbnail(
        self, 
        user_id: PydanticObjectId, 
        item_id: PydanticObjectId, 
        new_thumbnail: FileInput | None, 
        old_thumbnail: FileResponse | None = None,
        session=None
    ) -> None:
        if new_thumbnail is None:
            if old_thumbnail:
                try:
                    await self._storage_service.delete_file(old_thumbnail.key)
                except FileDeleteException:
                    pass
            await self._repo.update_own_by_id(user_id, item_id, {"thumbnail": None}, session=session)
            return None

        try:
            thumbnail = await self._storage_service.replace_file(
                new_file=new_thumbnail,
                destination_path=PermanentFileUploadPath.ITEM_THUMBNAIL.value,
                old_file=old_thumbnail,
            )
            await self._repo.update_own_by_id(
                user_id=user_id, 
                id=item_id, 
                data={"thumbnail": thumbnail.model_dump()}, 
                session=session
            )
            return thumbnail
        except FileReplaceException:
            return old_thumbnail

    
    async def _update_images(
        self, 
        user_id: PydanticObjectId, 
        item_id: PydanticObjectId, 
        new_images: list[FileInput], 
        old_images: list[FileResponse], 
        session=None
    ) -> None:
        final_images: list[FileResponse] = []
        for image in new_images:
            if image.url:
                final_images.append(FileResponse.model_validate(image))
            else:
                try:
                    new_image = await self._storage_service.finalize_file(image, PermanentFileUploadPath.ITEM_IMAGE.value)
                    new_images.append(FileResponse.model_validate(new_image))
                except FileFinalizeException:
                    pass

        for old_image in old_images:
            if not any(old_image.key == new_image.key for new_image in new_images):
                try:
                    await self._storage_service.delete_file(old_image.key)
                except FileDeleteException:
                    pass
                    
        await self._repo.update_own_by_id(
            user_id=user_id, 
            id=item_id, 
            data={"images": [image.model_dump() for image in final_images]}, 
            session=session
        )
        return final_images