from fastapi import Request

from app.modules.storage.service import StorageService


def get_storage_service(request: Request) -> StorageService:
    return StorageService(request.app.state.s3_client)
