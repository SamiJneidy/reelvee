"""OpenAPI documentation for item endpoints."""

from typing import Any
from fastapi import status

from app.shared.utils.docs import error_response

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.items.exceptions import ItemNotFoundException
from app.modules.storage.exceptions import FileDeleteException
from app.modules.users.exceptions import UserNotFoundException



# -------------------------------------------------------------------------
# Private (owner) routes — require authentication
# -------------------------------------------------------------------------

class ItemDocs:

    class ListOwnItems:
        summary = "List my items"
        description = (
            "Returns a paginated list of the authenticated user's items. "
            "Optional filters: type, name, category, status, visibility, slug."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnItem:
        summary = "Get my item by ID"
        description = "Returns a single item by ID. Only items owned by the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ItemNotFoundException),
        }

    class CreateItem:
        summary = "Create item"
        description = "Creates a new item for the authenticated user. Slug is generated from the item name."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class UpdateOwnItem:
        summary = "Update my item"
        description = "Updates an existing item by ID. Only provided fields are updated. Be careful when updating images, images with omitted or null URLs will be treated as new files. Item must belong to the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ItemNotFoundException),
        }

    class DeleteOwnItem:
        summary = "Delete my item"
        description = "Deletes an item by ID. Item must belong to the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ItemNotFoundException),
        }

    class DeleteOwnThumbnail:
        summary = "Delete my item's thumbnail"
        description = (
            "Deletes the thumbnail of an item and removes it from storage. "
            "If the item has no thumbnail, the request is ignored. "
            "Item must belong to the authenticated user."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ItemNotFoundException),
            status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(FileDeleteException),
        }


# -------------------------------------------------------------------------
# Public (storefront) routes — no authentication
# -------------------------------------------------------------------------

class ItemPublicDocs:

    class ListStoreItems:
        summary = "List store items"
        description = (
            "Returns a paginated list of items for a store, by store URL. "
            "Used for the public storefront. Optional filters: type, name, category, status, visibility, slug."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class GetStoreItemBySlug:
        summary = "Get store item by slug"
        description = "Returns a single item by slug for a given store (by store URL). Public endpoint for storefronts."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(
                UserNotFoundException,
                ItemNotFoundException,
                description="Store not found or item not found",
            ),
        }
