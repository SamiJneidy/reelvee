from fastapi import status

from app.core.exceptions.exceptions import BaseAppException


class CategoryNotFoundException(BaseAppException):
    detail = "Category not found"
    status_code = status.HTTP_404_NOT_FOUND


class CategoryAlreadyExistsException(BaseAppException):
    detail = "Category already exists"
    status_code = status.HTTP_409_CONFLICT
