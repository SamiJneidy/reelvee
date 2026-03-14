from app.core.exceptions.exceptions import BaseAppException
from fastapi import status

class InvalidFilenameException(BaseAppException):
    detail = "Invalid filename"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
