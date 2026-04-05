from fastapi import status

from app.core.exceptions.exceptions import BaseAppException

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


class UserNotVerifiedException(BaseAppException):
    detail = "Your account is not verified. Verify your account and try again."
    status_code = status.HTTP_403_FORBIDDEN


class SignUpNotCompletedException(BaseAppException):
    detail = "Your account setup is not complete. Please complete the sign up process to continue."
    status_code = status.HTTP_403_FORBIDDEN


class UserDeletedException(BaseAppException):
    detail = "Your account has been deleted. Please contact support to restore your account."
    status_code = status.HTTP_403_FORBIDDEN