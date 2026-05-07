"""OpenAPI documentation for invoice endpoints."""

from typing import Any

from fastapi import status

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.invoices.exceptions import (
    InvoiceAlreadyExistsForOrderException,
    InvoiceNotFoundException,
    InvoiceOrderNotCompletedException,
)
from app.modules.orders.exceptions import OrderNotFoundException
from app.shared.utils.docs import error_response


class InvoiceDocs:

    class ListOwnInvoices:
        summary = "List my invoices"
        description = (
            "Returns a paginated list of invoices for the authenticated store, "
            "sorted by most recent first. "
            "Optional filters: invoice_number, order_number, order_id, customer_id, item_id."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnInvoice:
        summary = "Get my invoice by ID"
        description = "Returns a single invoice by ID. Only invoices belonging to the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(InvoiceNotFoundException),
        }

    class CreateInvoice:
        summary = "Create invoice"
        description = (
            "Creates a new invoice for the authenticated store. "
            "Customer and items are resolved from the database (same pattern as manual orders). "
            "Optional ``order_id`` links the invoice to an order and copies its order number. "
            "Invoice number is assigned automatically in the format INV-000001."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class CreateInvoiceFromOrder:
        summary = "Create invoice from order"
        description = (
            "Creates an invoice from an existing order by ``order_id`` only. "
            "Copies customer, line items, and notes from the order; "
            "sets ``subtotal`` to the sum of line subtotals, ``discount`` to 0, and "
            "``total`` from the order (or the computed subtotal if the order total is unset). "
            "Invoice number is assigned automatically (e.g. INV-000001). "
            "At most one invoice per order."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_400_BAD_REQUEST: error_response(InvoiceOrderNotCompletedException),
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(OrderNotFoundException),
            status.HTTP_409_CONFLICT: error_response(InvoiceAlreadyExistsForOrderException),
        }

    class UpdateOwnInvoice:
        summary = "Update my invoice"
        description = (
            "Updates an existing invoice by ID. Only provided fields are updated. "
            "Invoice must belong to the authenticated store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(InvoiceNotFoundException),
        }

    class DeleteOwnInvoice:
        summary = "Delete my invoice"
        description = "Deletes an invoice by ID. Invoice must belong to the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(InvoiceNotFoundException),
        }
