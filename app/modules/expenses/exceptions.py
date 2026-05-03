from fastapi import status

from app.core.exceptions.exceptions import BaseAppException


class ExpenseNotFoundException(BaseAppException):
    detail = "Expense not found"
    status_code = status.HTTP_404_NOT_FOUND
