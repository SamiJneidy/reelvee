from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, example="Electronics")

    @field_validator("name", mode="after")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, example="Electronics")
