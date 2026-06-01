from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class FileUploadException(BaseAppException):
    detail = "Failed to generate upload URL"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class FileMoveException(BaseAppException):
    detail = "Failed to move file"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class FileDeleteException(BaseAppException):
    detail = "Failed to delete file"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

class FileFinalizeException(BaseAppException):
    detail = "Failed to finalize file"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

class FileReplaceException(BaseAppException):
    detail = "Failed to replace file"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR