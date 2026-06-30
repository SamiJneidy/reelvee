from fastapi import status

from app.core.exceptions.exceptions import BaseAppException


class GoogleOAuthNotConfiguredException(BaseAppException):
    detail = "Google OAuth is not configured on this server."
    status_code = status.HTTP_501_NOT_IMPLEMENTED

class GoogleOAuthException(BaseAppException):
    detail = "Google authentication failed. Please try again."
    status_code = status.HTTP_401_UNAUTHORIZED

class GoogleOAuthStateException(BaseAppException):
    detail = "Invalid or expired OAuth state. Please initiate the login again."
    status_code = status.HTTP_401_UNAUTHORIZED

class InvalidGoogleAuthTokenException(BaseAppException):
    detail = "Invalid or Expired Google auth token"
    status_code = status.HTTP_401_UNAUTHORIZED