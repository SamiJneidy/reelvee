"""OpenAPI documentation for user endpoints."""

from typing import Any
from fastapi import status

from app.core.exceptions.exceptions import DuplicateKeyErrorException
from app.shared.utils.docs import error_response

from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.storage.exceptions import FileDeleteException
from app.modules.users.exceptions import EmailChangeNotAllowedException, UserAlreadyCompletedException, UserNotFoundException, UserNotVerifiedException


class UserDocs:
    
    class SignUpComplete:
        summary = "Complete sign up"
        description = (
            "Completes the user profile after email verification. "
            "Requires a valid sign_up_complete_token cookie. "
            "Sets access_token and refresh_token cookies on success."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_400_BAD_REQUEST: error_response(
                UserAlreadyCompletedException,
                DuplicateKeyErrorException,
                description="User already completed or duplicate store link / whatsapp number",
            ),
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_403_FORBIDDEN: error_response(UserNotVerifiedException),
        }

    class UpdateUser:
        summary = "Update current user"
        description = (
            "Updates the authenticated user's profile fields. "
            "Only provided fields are updated (partial update)."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_400_BAD_REQUEST: error_response(
                DuplicateKeyErrorException,
                description="Some of the fields are already in use (email, store link, whatsapp number)",
            ),
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

    class DeleteOwnLogo:
        summary = "Delete current user logo"
        description = (
            "Deletes the authenticated user's logo from storage and "
            "clears the logo field on their profile."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
            status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(FileDeleteException),
        }

    class RequestEmailChange:
        summary = "Request email change link"
        description = (
            "Sends an email change confirmation link to the new email "
            "address. Requires the current password for verification."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(EmailChangeNotAllowedException),
        }

    class ConfirmEmailChange:
        summary = "Confirm email change"
        description = (
            "Confirms the email change using the token received via "
            "email. Reissues access_token and refresh_token cookies "
            "for the updated account."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(EmailChangeNotAllowedException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }
