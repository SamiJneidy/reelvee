import re
from typing import Any

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from fastapi import status
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.core.enums import PermanentFileUploadPath
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
from app.shared.utils.qrcode_helper import QRCodeUtils

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

        config = PageConfig(
            profile=ProfileConfig(title=profile_title, bio=profile_bio)
        )

        try:
            store = await self._repo.create(
                {
                    "user_id": user_id,
                    "store_url": store_url,
                    "links": links or [],
                    "qr_code": qr_code,
                    "logo": logo,
                    "config": config,
                },
                session=session,
            )
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise InvalidStoreUrlException(
                "Store URL is already in use", status.HTTP_409_CONFLICT
            )

        return StoreResponse.model_validate(store)

    # ------------------------------------------------------------------
    # Update
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

        update_data = data.model_dump(exclude_none=True, exclude={"logo"})

        try:
            await self._repo.update_by_user_id(user_id, update_data, session=session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise InvalidStoreUrlException(
                "Store URL is already in use", status.HTTP_409_CONFLICT
            )

        if data.logo is not None and not data.logo.url:
            await self._update_logo(user_id, data.logo, old_logo=store.logo, session=session)

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
        file: FileInput,
        old_logo,
        session=None,
    ) -> FileResponse:
        if file.url:
            logo_data = FileResponse.model_validate(file)
        else:
            logo_data = FileResponse.model_validate(
                await self._storage_service.finalize_file(
                    file=file,
                    destination_path=PermanentFileUploadPath.USER_LOGO.value,
                )
            )
            if old_logo:
                try:
                    await self._storage_service.delete_file(old_logo.key)
                except Exception:
                    pass
        await self._repo.update_by_user_id(user_id, {"logo": logo_data}, session=session)
        return logo_data

    async def _generate_qr_code(self, store_url: str, session=None) -> FileResponse:
        qr_bytes = QRCodeUtils.generate_qr_code(store_url)
        data = await self._storage_service.upload_bytes(
            path=PermanentFileUploadPath.USER_QR_CODE.value,
            filename=f"{store_url.rsplit('/', 1)[-1]}.png",
            content=qr_bytes,
        )
        return FileResponse.model_validate(data)
