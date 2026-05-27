from typing import AsyncGenerator

from fastapi import Depends, Request

from app.modules.storage.service import StorageService

async def get_s3_client(request: Request) -> AsyncGenerator:
    return request.app.state.s3_client

def get_storage_service(
    s3_client = Depends(get_s3_client),
) -> StorageService:
    return StorageService(s3_client)
