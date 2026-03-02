from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SingleObjectResponse(BaseModel, Generic[T]):
    """Wrapper for a single resource in JSON responses."""
    data: T


class SuccessResponse(BaseModel):
    detail: str


class ErrorResponse(BaseModel):
    detail: str
