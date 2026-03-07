from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class EmailCouldNotBeSentException(BaseAppException):
    detail = "Email could not be sent"
    status_code = status.HTTP_408_REQUEST_TIMEOUT
