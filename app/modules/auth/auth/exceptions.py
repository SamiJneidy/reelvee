from fastapi import status

from app.core.exceptions.exceptions import BaseAppException
from app.modules.users.exceptions import (
    UserAlreadyExistsException,
    UserBlockedException,
    UserDisabledException,
    UserNotActiveException,
    UserNotFoundException,
    UserNotVerifiedException,
)


class PasswordResetNotAllowedException(BaseAppException):
    detail = (
        "Password reset not allowed. This may happen because of invlid or expired OTP code "
        "or for other security issues. Please request a new OTP code and try again."
    )
    status_code = status.HTTP_401_UNAUTHORIZED


class PasswordsDontMatchException(BaseAppException):
    detail = "Passwords don't match"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidCredentialsException(BaseAppException):
    detail = "Invalid credentials"
    status_code = status.HTTP_401_UNAUTHORIZED


class UserAlreadyCompletedException(BaseAppException):
    detail = "User already completed"
    status_code = status.HTTP_400_BAD_REQUEST


class DuplicateKeyErrorException(BaseAppException):
    detail = "Duplicate key error"
    status_code = status.HTTP_400_BAD_REQUEST


class EmailChangeNotAllowedException(BaseAppException):
    detail = "Email change not allowed"
    status_code = status.HTTP_401_UNAUTHORIZED
