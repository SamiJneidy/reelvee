from fastapi import status
from app.core.exceptions.exceptions import BaseAppException

class EmailCouldNotBeSentException(BaseAppException):
    """Raised when the email could not be sent."""
    def __init__(self, detail: str | None = "Email could not be sent", status_code: int = status.HTTP_408_REQUEST_TIMEOUT):
        super().__init__(detail, status_code)
