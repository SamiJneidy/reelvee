from typing import Any
from fastapi import status

from app.shared.utils.docs import error_response
from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.storage.exceptions import FileUploadException


class StorageDocs:

    class UploadFile:
        summary = "Request a file upload URL"
        description = (
            "Generates a presigned S3 URL for direct file upload from the client. "
            "The client uploads the file directly to S3 using the returned URL, "
            "then submits the returned id and key when creating or updating a resource."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(FileUploadException),
        }

    class UploadFileDirect:
        summary = "Upload a file directly to S3"
        description = (
            "Uploads a file directly to temporary S3 storage. "
            "Returns the id and key to submit when creating or updating a resource."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(FileUploadException),
        }
