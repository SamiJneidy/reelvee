import re
from typing import Any

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from fastapi import status
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.enums import (
    BackgroundType,
    ButtonShape,
    ButtonVariant,
    Font,
    Layout,
    PermanentFileUploadPath,
    TemplateId,
)
from app.modules.storage.models import File
from app.modules.storage.schemas import FileInput, FileResponse
from app.modules.storage.service import StorageService
from app.modules.store.exceptions import (
    InvalidStoreUrlException,
    StoreAlreadyExistsException,
    StoreNotFoundException,
)
from app.modules.store.models import PageConfig, ProfileConfig, ThemeConfig
from app.modules.store.repository import StoreRepository
from app.modules.store.schemas import StoreResponse, StoreUpdate
from app.modules.store.schemas.base import StoreBase
from app.shared.utils.qrcode_helper import QRCodeUtils


def _file_from_response(fr: FileResponse | None) -> File | None:
    if fr is None:
        return None
    return File.model_validate(fr.model_dump())


class StoreService:
    def __init__(
        self,
        repo: StoreRepository,
        storage_service: StorageService,
    ) -> None:
        self._repo = repo
        self._storage_service = storage_service

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def get_by_user_id(self, user_id: PydanticObjectId) -> StoreResponse:
        store = await self._repo.get_by_user_id(user_id)
        if not store:
            raise StoreNotFoundException()
        return StoreResponse.model_validate(store)

    async def get_by_store_url(self, store_url: str) -> StoreResponse:
        store = await self._repo.get_by_store_url(store_url)
        if not store:
            raise StoreNotFoundException()
        return StoreResponse.model_validate(store)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    async def validate_store_url(
        self,
        store_url: str,
        current_user_id: PydanticObjectId | None = None,
        session=None,
    ) -> None:
        if len(store_url) < 3:
            raise InvalidStoreUrlException("Store URL must be at least 3 characters long")
        if not re.match(r'^[a-z0-9-]+$', store_url.strip().lower()):
            raise InvalidStoreUrlException(
                "Store URL can only contain lowercase letters, numbers, and hyphens"
            )
        existing = await self._repo.get_by_store_url(store_url, session=session)
        if existing and existing.user_id != current_user_id:
            raise InvalidStoreUrlException(
                "Store URL is already in use", status.HTTP_409_CONFLICT
            )

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create_for_user(
        self,
        user_id: PydanticObjectId,
        store_url: str,
        profile_title: str = "",
        profile_bio: str = "",
        links: list | None = None,
        logo: FileInput | None = None,
        session=None,
    ) -> StoreResponse:
        if await self._repo.get_by_user_id(user_id, session=session):
            raise StoreAlreadyExistsException()

        await self.validate_store_url(store_url, current_user_id=user_id, session=session)
        store_url = store_url.strip().lower()

        qr_code = await self._generate_qr_code(self._get_full_store_url(store_url), session=session)

        store_base = StoreBase(store_url=store_url, links=links or [])
        data = store_base.model_dump()
        data.update({"user_id": user_id, "qr_code": qr_code})

        try:
            store = await self._repo.create(data, session=session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise InvalidStoreUrlException(
                "Store URL is already in use", status.HTTP_409_CONFLICT
            )

        if logo:
            await self._update_logo(user_id, logo, session=session)

        return StoreResponse.model_validate(store)

    # ------------------------------------------------------------------
    # Update (full body PUT)
    # ------------------------------------------------------------------

    async def update_by_user_id(
        self,
        user_id: PydanticObjectId,
        data: StoreUpdate,
        session=None,
    ) -> StoreResponse:
        store = await self._repo.get_by_user_id(user_id, session=session)
        if not store:
            raise StoreNotFoundException()

        update_data = data.model_dump()
        
        logo = await self._handle_logo_update(data, store.logo)
        update_data["logo"] = logo
        
        background_image = await self._handle_background_image_update(data, store.config.theme.background_image)
        if update_data.get("config") and update_data["config"].get("theme"):
            update_data["config"]["theme"]["background_image"] = background_image

        try:
            await self._repo.update_by_user_id(user_id, update_data, session=session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise InvalidStoreUrlException(
                "Store URL is already in use", status.HTTP_409_CONFLICT
            )

        return StoreResponse.model_validate(
            await self._repo.get_by_user_id(user_id, session=session)
        )

    # ------------------------------------------------------------------
    # Logo
    # ------------------------------------------------------------------

    async def update_logo(
        self, user_id: PydanticObjectId, file: FileInput, session=None
    ) -> FileResponse:
        store = await self._repo.get_by_user_id(user_id, session=session)
        if not store:
            raise StoreNotFoundException()
        return await self._update_logo(user_id, file, old_logo=store.logo, session=session)

    async def delete_logo(self, user_id: PydanticObjectId, session=None) -> None:
        store = await self._repo.get_by_user_id(user_id, session=session)
        if not store:
            raise StoreNotFoundException()
        if store.logo:
            try:
                await self._storage_service.delete_file(store.logo.key)
            except Exception:
                pass
        await self._repo.update_by_user_id(user_id, {"logo": None}, session=session)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    
    def _get_full_store_url(self, store_url: str) -> str:
        return f"{settings.frontend_url}/@{store_url}"

    async def _update_logo(
        self,
        user_id: PydanticObjectId,
        new_logo: FileInput | None,
        old_logo: FileResponse | None,
        session=None,
    ) -> FileResponse:
        if new_logo is None:
            await self._repo.update_by_user_id(user_id, {"logo": None}, session=session)
            if old_logo:
                await self._storage_service.delete_file(old_logo.key)
        try:
            logo = await self._storage_service.replace_file(
                new_file=new_logo,
                destination_path=PermanentFileUploadPath.STORE_LOGO.value,
                old_file=old_logo,
            )
        except Exception as e:
            logo = old_logo
        
        await self._repo.update_by_user_id(user_id, {"logo": logo.model_dump()}, session=session)
        return logo


    async def _handle_logo_update(self, data: StoreUpdate, old_logo = None) -> FileResponse | None:
        if "logo" not in data.model_fields_set:
            return old_logo

        if data.logo is None:
            if old_logo:
                await self._storage_service.delete_file(old_logo.key)
            return None

        logo = old_logo
        if logo is not None and logo.url is None:
            try:
                logo = await self._storage_service.finalize_file(
                    file=data.logo,
                    destination_path=PermanentFileUploadPath.STORE_LOGO.value
                )
                if old_logo:
                    try:
                        await self._storage_service.delete_file(old_logo.key)
                    except Exception:
                        pass
            except Exception as e:
                logo = old_logo
        return logo


    async def _handle_background_image_update(self, data: StoreUpdate, old_image = None) -> FileResponse | None:
        if not data.config or not data.config.theme or "background_image" not in data.config.theme.model_fields_set:
            return old_image

        if data.config.theme.background_image is None:
            if old_image:
                await self._storage_service.delete_file(old_image.key)
            return None

        image = old_image
        if image is not None and image.url is None:
            try:
                image = await self._storage_service.finalize_file(
                    file=data.config.theme.background_image,
                    destination_path=PermanentFileUploadPath.STORE_BACKGROUND_IMAGE.value
                )
                if old_image:
                    try:
                        await self._storage_service.delete_file(old_image.key)
                    except Exception:
                        pass
            except Exception as e:
                image = old_image
        return image


    async def _generate_qr_code(self, store_url: str, session=None) -> FileResponse:
        qr_bytes = QRCodeUtils.generate_qr_code(store_url)
        data = await self._storage_service.upload_bytes(
            path=PermanentFileUploadPath.STORE_QR_CODE.value,
            filename=f"{store_url.rsplit('/', 1)[-1]}.png",
            content=qr_bytes,
        )
        return FileResponse.model_validate(data)
