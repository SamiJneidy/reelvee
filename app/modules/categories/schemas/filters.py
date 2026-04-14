from pydantic import BaseModel


class CategoryFilters(BaseModel):
    name: str | None = None
