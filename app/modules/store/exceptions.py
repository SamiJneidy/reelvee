from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class StoreNotFoundException(BaseAppException):
    detail = "Store not found"
    status_code = status.HTTP_404_NOT_FOUND


class StoreAlreadyExistsException(BaseAppException):
    detail = "A store already exists for this user"
    status_code = status.HTTP_409_CONFLICT


class InvalidStoreUrlException(BaseAppException):
    detail = "The store URL is invalid or already in use"
    status_code = status.HTTP_400_BAD_REQUEST
