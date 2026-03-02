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


# Auth
class PasswordResetNotAllowedException(BaseAppException):
    """Raised when trying to reset the password without verifying the OTP code or the email is blocked."""
    def __init__(self, detail: str | None = "Password reset not allowed. This may happen because of invlid or expired OTP code or for other security issues. Please request a new OTP code and try again.", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class PasswordsDontMatchException(BaseAppException):
    """Raised when reseting the password and the provided passwords don't match."""
    def __init__(self, detail: str | None = "Passwords don't match", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class InvalidCredentialsException(BaseAppException):
    """Raised when trying to login but the credentials are invalid."""
    def __init__(self, detail: str | None = "Invalid credentials", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class UserAlreadyCompletedException(BaseAppException):
    """Raised when trying to complete the sign up but the user is already completed."""
    def __init__(self, detail: str | None = "User already completed", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class DuplicateKeyErrorException(BaseAppException):
    """Raised when a duplicate key error occurs."""
    def __init__(self, detail: str | None = "Duplicate key error", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(detail, status_code)

class EmailChangeNotAllowedException(BaseAppException):
    """Raised when the email change is not allowed."""
    def __init__(self, detail: str | None = "Email change not allowed", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)