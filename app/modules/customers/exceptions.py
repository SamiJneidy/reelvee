from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class CustomerNotFoundException(BaseAppException):
    detail = "Customer not found"
    status_code = status.HTTP_404_NOT_FOUND


class CustomerAlreadyExistsException(BaseAppException):
    detail = "A customer with this phone number already exists in your store"
    status_code = status.HTTP_409_CONFLICT
