from fastapi import Depends
from typing import Annotated

from app.modules.storage.dependencies import StorageService, get_storage_service
from app.modules.store.repository import StoreRepository
from app.modules.store.service import StoreService


def get_store_repository() -> StoreRepository:
    return StoreRepository()


def get_store_service(
    repo: Annotated[StoreRepository, Depends(get_store_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> StoreService:
    return StoreService(repo, storage_service)
