from fastapi import status
from app.core.exceptions.exceptions import BaseAppException


class InvalidOTPException(BaseAppException):
    detail = "The OTP code is invalid or has expired or has been used before"
    status_code = status.HTTP_401_UNAUTHORIZED


class OTPExpiredException(BaseAppException):
    detail = "OTP code has expired"
    status_code = status.HTTP_401_UNAUTHORIZED


class OTPAlreadyUsedException(BaseAppException):
    detail = "The OTP code has been used before"
    status_code = status.HTTP_401_UNAUTHORIZED


class SuspiciousOTPActivityException(BaseAppException):
    detail = "Suspicious activiy has been detected. Operation aborted for security issues."
    status_code = status.HTTP_403_FORBIDDEN


class OTPNotFoundException(BaseAppException):
    detail = "OTP not found"
    status_code = status.HTTP_404_NOT_FOUND


class OTPCouldNotBeSentException(BaseAppException):
    detail = "OTP could not be sent to the email"
    status_code = status.HTTP_408_REQUEST_TIMEOUT
