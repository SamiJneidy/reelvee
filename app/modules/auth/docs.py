"""OpenAPI documentation for auth endpoints."""

from typing import Any
from fastapi import status

from app.shared.utils.docs import error_response

from app.modules.auth.exceptions import (
    InvalidCredentialsException,
    PasswordResetNotAllowedException,
)
from app.modules.auth.otp.exceptions import (
    InvalidOTPException,
    OTPCouldNotBeSentException,
)
from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.users.exceptions import (
    UserAlreadyExistsException,
    UserBlockedException,
    UserDisabledException,
    UserNotActiveException,
    UserNotFoundException,
    UserNotVerifiedException,
)


class AuthDocs:

    class GetMe:
        summary = "Get current session"
        description = (
            "Retrieves the current user's session data based on the "
            "provided authentication cookies."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class Signup:
        summary = "Register a new account"
        description = (
            "Creates a new user account in PENDING state and "
            "automatically sends an email verification OTP."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_409_CONFLICT: error_response(UserAlreadyExistsException),
        }


    class Login:
        summary = "Authenticate with email and password"
        description = (
            "Validates credentials and returns the user data. "
            "On success for a fully completed account, sets access_token "
            "and refresh_token as HTTP-only cookies. "
            "If the email is not yet verified, a verification OTP is "
            "sent automatically. If the profile is incomplete, a "
            "sign_up_complete_token cookie is set instead."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidCredentialsException),
            status.HTTP_403_FORBIDDEN: error_response(
                UserDisabledException,
                UserBlockedException,
                UserNotVerifiedException,
                UserNotActiveException,
                description="Account is disabled, blocked, not verified, or not active",
            ),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class Refresh:
        summary = "Refresh access token"
        description = (
            "Reads the refresh_token cookie and issues a new "
            "access_token cookie."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidTokenException),
        }

    class Logout:
        summary = "Logout"
        description = "Clears the access_token and refresh_token cookies."

    class RequestEmailVerification:
        summary = "Request email verification OTP"
        description = (
            "Sends a one-time password to the provided email address "
            "for email verification purposes."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
            status.HTTP_408_REQUEST_TIMEOUT: error_response(OTPCouldNotBeSentException),
        }

    class VerifyEmail:
        summary = "Verify email with OTP"
        description = (
            "Verifies the user's email address using the OTP code. "
            "If the profile is not yet completed, a sign_up_complete_token "
            "cookie is set."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidOTPException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class RequestPasswordReset:
        summary = "Request password reset link"
        description = "Sends a password reset link to the provided email address."
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class ResetPassword:
        summary = "Reset password"
        description = (
            "Resets the user's password using a password-reset token "
            "received via email. Also resets invalid login attempts."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(PasswordResetNotAllowedException),
            status.HTTP_404_NOT_FOUND: error_response(UserNotFoundException),
        }

    class SwaggerLogin:
        summary = "Swagger login"
        description = (
            "OAuth2-compatible login endpoint for the Swagger UI. "
            "Returns a bearer token for use in the Authorize dialog."
        )
        responses: dict[int | str, dict[str, Any]] = {
            status.HTTP_401_UNAUTHORIZED: error_response(InvalidCredentialsException),
            status.HTTP_403_FORBIDDEN: error_response(
                UserDisabledException,
                UserBlockedException,
                UserNotVerifiedException,
                description="Account is disabled, blocked, or not verified",
            ),
        }
