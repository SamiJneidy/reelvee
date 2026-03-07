from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class InvalidTokenException(BaseAppException):
    detail = "Invalid token"
    status_code = status.HTTP_401_UNAUTHORIZED
