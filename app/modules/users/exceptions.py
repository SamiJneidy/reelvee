from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class UserAlreadyExistsException(BaseAppException):
    detail = "Email already in use"
    status_code = status.HTTP_409_CONFLICT


class UserNotFoundException(BaseAppException):
    detail = "User not found"
    status_code = status.HTTP_404_NOT_FOUND


class UserNotActiveException(BaseAppException):
    detail = "Your accounts is not active. You can not perform the action."
    status_code = status.HTTP_403_FORBIDDEN


class UserNotCompleteException(BaseAppException):
    detail = "The user has not completed the sign up."
    status_code = status.HTTP_403_FORBIDDEN


class UserBlockedException(BaseAppException):
    detail = "Your accounts is blocked. Please contact the support to discuss the issue."
    status_code = status.HTTP_403_FORBIDDEN


class UserDisabledException(BaseAppException):
    detail = (
        "Your account is disabled. This usually happens due to security reasons "
        "or multiple invalid login attempts. Please reset your password and try again."
    )
    status_code = status.HTTP_403_FORBIDDEN


class UserNotPendingException(BaseAppException):
    detail = "User status is not pending to verify the email"
    status_code = status.HTTP_400_BAD_REQUEST


class UserNotVerifiedException(BaseAppException):
    detail = "Your account is not verified. Verify your account and try again."
    status_code = status.HTTP_403_FORBIDDEN


class InvitationNotAllowedException(BaseAppException):
    detail = "Invitation not allowed. This may happen because the user is already set up or blocked."
    status_code = status.HTTP_403_FORBIDDEN


class InvalidStoreLinkException(BaseAppException):
    detail = "The store link is invalid or not available"
    status_code = status.HTTP_400_BAD_REQUEST


class EmailChangeNotAllowedException(BaseAppException):
    detail = "Email change not allowed"
    status_code = status.HTTP_401_UNAUTHORIZED


class UserAlreadyCompletedException(BaseAppException):
    detail = "User already completed"
    status_code = status.HTTP_400_BAD_REQUEST
