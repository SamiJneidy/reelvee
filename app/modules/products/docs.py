"""OpenAPI documentation for product endpoints."""

from typing import Any
from fastapi import status

from app.shared.docs import error_response

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.products.exceptions import ProductNotFoundException
from app.modules.users.exceptions import UserNotFoundException


# -------------------------------------------------------------------------
# Private (owner) routes — require authentication
# -------------------------------------------------------------------------

class ProductDocs:

    class ListOwnProducts:
        summary = "List my products"
        description = (
            "Returns a paginated list of the authenticated user's products. "
            "Optional filters: name, category, status, visibility, slug."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class GetOwnProduct:
        summary = "Get my product by ID"
        description = "Returns a single product by ID. Only products owned by the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ProductNotFoundException),
        }

    class CreateProduct:
        summary = "Create product"
        description = "Creates a new product for the authenticated user. Slug is generated from the product name."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class UpdateOwnProduct:
        summary = "Update my product"
        description = "Updates an existing product by ID. Only provided fields are updated. Product must belong to the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ProductNotFoundException),
        }

    class DeleteOwnProduct:
        summary = "Delete my product"
        description = "Deletes a product by ID. Product must belong to the authenticated user."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(ProductNotFoundException),
        }


# -------------------------------------------------------------------------
# Public (storefront) routes — no authentication
# -------------------------------------------------------------------------

class ProductPublicDocs:

    class ListStoreProducts:
        summary = "List store products"
        description = (
            "Returns a paginated list of products for a store, by store URL. "
            "Used for the public storefront. Optional filters: name, category, status, visibility, slug."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class GetStoreProductBySlug:
        summary = "Get store product by slug"
        description = "Returns a single product by slug for a given store (by store URL). Public endpoint for storefronts."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(
                UserNotFoundException,
                ProductNotFoundException,
                description="Store not found or product not found",
            ),
        }
