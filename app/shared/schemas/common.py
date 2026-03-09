from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class Link(BaseModel):
    name: str = Field(..., example="Instagram")
    url: str = Field(..., example="https://www.instagram.com/your_username")

class TimeMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class BaseModelWithId(BaseModel):
    id: str

    @field_validator("id", mode="before")
    @classmethod
    def id_to_str(cls, v):
        return str(v) if v is not None else v
        