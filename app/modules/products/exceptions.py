from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class ProductNotFoundException(BaseAppException):
    detail = "Product not found"
    status_code = status.HTTP_404_NOT_FOUND
