from fastapi import status


class BaseAppException(Exception):
    detail: str = "An error has occurred."
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        self.detail = detail or self.__class__.detail
        self.status_code = status_code or self.__class__.status_code


class RequestCouldNotBeSent(BaseAppException):
    detail = "Request could not be sent."
    status_code = status.HTTP_408_REQUEST_TIMEOUT


class IntegrityErrorException(BaseAppException):
    detail = (
        "A database integrity error occurred. "
        "This may be due to a unique, foreign key, not-null, or check constraint violation."
    )
    status_code = status.HTTP_400_BAD_REQUEST


class UniqueConstraintViolationException(BaseAppException):
    detail = "Unique constraint violation: A record with the same unique value already exists."
    status_code = status.HTTP_409_CONFLICT


class ForeignKeyViolationException(BaseAppException):
    detail = "Foreign key constraint violation: Referenced record does not exist."
    status_code = status.HTTP_400_BAD_REQUEST


class NotNullConstraintViolationException(BaseAppException):
    detail = "Not-null constraint violation: A required field was left null."
    status_code = status.HTTP_400_BAD_REQUEST


class CheckConstraintViolationException(BaseAppException):
    detail = "Check constraint violation: A column value failed a custom validation rule."
    status_code = status.HTTP_400_BAD_REQUEST
