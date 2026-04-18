"""OpenAPI documentation for invoice endpoints."""

from typing import Any

from fastapi import status

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.invoices.exceptions import InvoiceNotFoundException
from app.shared.utils.docs import error_response


class InvoiceDocs:

    class ListOwnInvoices:
        summary = "List my invoices"
        description = (
            "Returns a paginated list of invoices for the authenticated store, "
            "sorted by most recent first. "
            "Optional filters: invoice_number, order_number, order_reference_number, currency."
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
            "Invoice number is assigned automatically in the format INV-000001."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
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
