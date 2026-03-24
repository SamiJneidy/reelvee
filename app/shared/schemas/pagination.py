from pydantic import BaseModel, Field
from typing import Any

from typing import Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total_rows: int | None = None
    total_pages: int | None = None
    page: int | None = None
    limit: int | None = None

class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)

    @property
    def skip(self):
        if self.page is not None and self.limit is not None:
            return (self.page-1) * self.limit
        return None
        