from fastapi import status
from app.core.exceptions.exceptions import BaseAppException

class InvalidOTPException(BaseAppException):
    """Raised when the OTP code is invalid."""
    def __init__(self, detail: str | None = "The OTP code is invalid or has expired or has been used before", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class OTPExpiredException(BaseAppException):
    """Raised when the OTP code is expired."""
    def __init__(self, detail: str | None = "OTP code has expired", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class OTPAlreadyUsedException(BaseAppException):
    """Raised when the OTP has already been used and cannot be reused."""
    def __init__(self, detail: str | None = "The OTP code has been used before", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(detail, status_code)

class SuspiciousOTPActivityException(BaseAppException):
    """Raised when a security issue is detected with the OTP process."""
    def __init__(self, detail: str | None = "Suspicious activiy has been detected. Operation aborted for security issues.", status_code: int = status.HTTP_403_FORBIDDEN):
        super().__init__(detail, status_code)

class OTPNotFoundException(BaseAppException):
    """Raised when the OTP is not found."""
    def __init__(self, detail: str | None = "OTP not found", status_code: int = status.HTTP_404_NOT_FOUND):
        super().__init__(detail, status_code)

class OTPCouldNotBeSentException(BaseAppException):
    """Raised when the OTP could not be sent to the email."""
    def __init__(self, detail: str | None = "OTP could not be sent to the email", status_code: int = status.HTTP_408_REQUEST_TIMEOUT):
        super().__init__(detail, status_code)

