"""OpenAPI documentation for order endpoints."""

from typing import Any
from fastapi import status

from app.shared.utils.docs import error_response
from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.items.exceptions import ItemNotFoundException
from app.modules.orders.exceptions import ItemNotBelongToUserException, OrderNotFoundException
from app.modules.users.exceptions import UserNotFoundException


class OrderDocs:

    class ListOwnOrders:
        summary = "List my orders"
        description = (
            "Returns a paginated list of orders for the authenticated store, "
            "sorted by most recent first. "
            "Optional filters: status, is_read, source, customer_id, item_id, delivery_status, payment_status."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnOrder:
        summary = "Get my order by ID"
        description = "Returns a single order by ID. Only orders belonging to the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(OrderNotFoundException),
        }

    class GetUnreadCount:
        summary = "Get unread orders count"
        description = "Returns the count of unread orders for the authenticated store. Use this to drive dashboard notification badges."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class CreateOrder:
        summary = "Create order"
        description = (
            "Manually creates a new order for the authenticated store. "
            "Source is automatically set to 'internal' and is_read to true. "
            "Status defaults to 'new'."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class UpdateOwnOrder:
        summary = "Update my order"
        description = (
            "Updates an existing order by ID. Only provided fields are updated. "
            "Order must belong to the authenticated store."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(OrderNotFoundException),
        }

    class DeleteOwnOrder:
        summary = "Delete my order"
        description = "Deletes an order by ID. Order must belong to the authenticated store."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(OrderNotFoundException),
        }


class OrderPublicDocs:

    class CreatePublicOrder:
        summary = "Submit an order"
        description = (
            "Submits a new order for a store identified by its store URL. "
            "A customer record is created automatically if the phone number is not already on file. "
            "No authentication required. "
            "The order is created with status 'new' and will appear in the store owner's dashboard."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(
                UserNotFoundException,
                ItemNotFoundException,
                description="Store not found or item not found / not available",
            ),
            status.HTTP_403_FORBIDDEN: error_response(ItemNotBelongToUserException),
        }
