"""OpenAPI documentation for category endpoints."""

from typing import Any

from fastapi import status

from app.modules.categories.exceptions import CategoryAlreadyExistsException, CategoryNotFoundException
from app.shared.utils.docs import error_response


class CategoryDocs:
    class ListCategories:
        summary = "List categories"
        description = (
            "Returns a paginated list of categories sorted by name. "
            "Use query parameters `page`, `limit`, and optional `name` for filtering."
        )

    class GetCategory:
        summary = "Get category by ID"
        description = "Returns a single category by ID."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(CategoryNotFoundException),
        }

    class CreateCategory:
        summary = "Create category"
        description = "Creates a new category."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_409_CONFLICT: error_response(CategoryAlreadyExistsException),
        }

    class UpdateCategory:
        summary = "Update category"
        description = "Updates an existing category by ID."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(CategoryNotFoundException),
            status.HTTP_409_CONFLICT: error_response(CategoryAlreadyExistsException),
        }

    class DeleteCategory:
        summary = "Delete category"
        description = "Deletes a category by ID."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(CategoryNotFoundException),
        }
