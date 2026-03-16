from token import EXACT_TOKEN_TYPES
import httpx
import boto3
import mimetypes
import uuid

from app.core.config import settings
from app.modules.storage.exceptions import FileDeleteException, FileMoveException, FileUploadException
from app.modules.storage.schemas import FileInput, FileResponse, PresignedURLResponse
from app.shared.utils.file_helper import FileHelper

class StorageService:


    def __init__(self, s3_client: boto3.client) -> None:
        self.s3_client = s3_client


    def get_file_url(self, file_key: str) -> str:
        """Get the URL of a file in S3"""
        return f"https://{settings.aws_bucket}.s3.amazonaws.com/{file_key}"


    async def generate_upload_url(self, path: str, filename: str, content_type: str = None) -> PresignedURLResponse:
        extension = FileHelper.get_extension(filename)
        file_id = str(uuid.uuid4())
        file_key = f"{path}/{file_id}.{extension}"
        content_type = content_type or mimetypes.guess_type(filename)[0]
        try:
            upload_url = await self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": settings.aws_bucket,
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=settings.aws_presigned_url_expiration_seconds,
            )
        except Exception:
            raise FileUploadException()
        return PresignedURLResponse(id=file_id, key=file_key, upload_url=upload_url)


    async def upload_bytes(
        self,
        path: str,
        filename: str,
        content: bytes,
        content_type: str | None = None,
    ) -> FileResponse:
        """Upload bytes to S3 and return the file key"""
        extension = FileHelper.get_extension(filename)
        file_id = str(uuid.uuid4())
        file_key = f"{path}/{file_id}.{extension}"
        content_type = content_type or mimetypes.guess_type(filename)[0]
        try:
            await self.s3_client.put_object(
                Bucket=settings.aws_bucket,
                Key=file_key,
                Body=content,
                ContentType=content_type,
            )
        except Exception:
            raise FileUploadException()
        url = self.get_file_url(file_key)
        return FileResponse(id=file_id, key=file_key, url=url)


    async def upload_file(
        self,
        presigned_response: dict,
        content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> FileInput:
        """Upload file to S3 using presigned URL and return the file response"""
        file_id = presigned_response["id"]
        file_key = presigned_response["key"]
        upload_url = presigned_response["upload_url"]
        content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    upload_url,
                    content=content,
                    headers={"Content-Type": content_type},
                )
            if response.status_code not in (200, 204):
                raise FileUploadException()
        except Exception:
            raise FileUploadException()
        return FileInput(id=file_id, key=file_key)


    async def move_file(self, source_key: str, destination_key: str) -> None:
        try:
            await self.s3_client.copy_object(
                Bucket=settings.aws_bucket,
                CopySource=f"{settings.aws_bucket}/{source_key}",
                Key=destination_key,
            )
            await self.s3_client.delete_object(
                Bucket=settings.aws_bucket,
                Key=source_key,
            )
        except Exception:
            raise FileMoveException()


    async def finalize_file(self, file: FileInput, destination_path: str) -> FileResponse:
        if file.url:
            return file
        extension = file.key.split(".")[-1]
        destination_key = f"{destination_path}/{file.id}.{extension}"
        await self.move_file(file.key, destination_key)
        return FileResponse(id=file.id, key=destination_key, url=self.get_file_url(destination_key))


    async def delete_file(self, key: str) -> None:
        try:
            await self.s3_client.delete_object(
                Bucket=settings.aws_bucket,
                Key=key,
            )
        except Exception:
            raise FileDeleteException()
