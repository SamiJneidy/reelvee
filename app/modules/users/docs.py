"""OpenAPI documentation for user endpoints."""

from typing import Any
from fastapi import status

from app.shared.docs import error_response

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.users.exceptions import UserNotFoundException


class UserDocs:

    class UpdateUser:
        summary = "Update current user"
        description = (
            "Updates the authenticated user's profile fields. "
            "Only provided fields are updated (partial update)."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class SoftDeleteUser:
        summary = "Soft delete current user"
        description = (
            "Marks the authenticated user's account as deleted. "
            "The account data is retained but the user can no longer "
            "access it."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }
