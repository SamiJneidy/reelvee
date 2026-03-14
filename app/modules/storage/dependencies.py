import aioboto3
from typing import Annotated, AsyncGenerator

from fastapi import Depends

from app.core.config import settings
from app.modules.storage.service import StorageService


async def get_s3_client() -> AsyncGenerator:
    async with aioboto3.Session().client(
        "s3",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    ) as client:
        yield client


def get_storage_service(
    s3_client = Depends(get_s3_client),
) -> StorageService:
    return StorageService(s3_client)
