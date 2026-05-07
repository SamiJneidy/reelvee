from fastapi import status

from app.core.exceptions.exceptions import BaseAppException


class InvoiceNotFoundException(BaseAppException):
    detail = "Invoice not found"
    status_code = status.HTTP_404_NOT_FOUND


class InvoiceAlreadyExistsForOrderException(BaseAppException):
    detail = "An invoice already exists for this order"
    status_code = status.HTTP_409_CONFLICT


class InvoiceOrderNotCompletedException(BaseAppException):
    detail = "The order data is not complete. Cannot create an invoice for an order that is not completed"
    status_code = status.HTTP_400_BAD_REQUEST