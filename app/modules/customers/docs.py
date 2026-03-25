"""OpenAPI documentation for customer endpoints."""

from typing import Any
from fastapi import status

from app.shared.utils.docs import error_response
from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.customers.exceptions import (
    CustomerAlreadyExistsException,
    CustomerNotFoundException,
)


class CustomerDocs:

    class ListOwnCustomers:
        summary = "List my customers"
        description = (
            "Returns a paginated list of customers belonging to the authenticated store. "
            "Optional filters: name, phone, email, is_favourite, status, source."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnCustomer:
        summary = "Get my customer by ID"
        description = "Returns a single customer by ID. Only customers belonging to the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(CustomerNotFoundException),
        }

    class CreateCustomer:
        summary = "Create customer"
        description = (
            "Manually creates a new customer for the authenticated store. "
            "Source is automatically set to 'internal'. "
            "Phone number must be unique within the store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_409_CONFLICT: error_response(CustomerAlreadyExistsException),
        }

    class UpdateOwnCustomer:
        summary = "Update my customer"
        description = (
            "Updates an existing customer by ID. Only provided fields are updated. "
            "Customer must belong to the authenticated store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(CustomerNotFoundException),
            status.HTTP_409_CONFLICT: error_response(CustomerAlreadyExistsException),
        }

    class DeleteOwnCustomer:
        summary = "Delete my customer"
        description = (
            "Deletes a customer by ID. Customer must belong to the authenticated store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(CustomerNotFoundException),
        }
