from fastapi import status
from app.core.exceptions.exceptions import BaseAppException

class InvalidTokenException(BaseAppException):
    """Raised the token is invalid or expired."""
    def __init__(self, detail: str | None = "Invalid token", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)