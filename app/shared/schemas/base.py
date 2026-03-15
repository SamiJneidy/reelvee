from pydantic import BaseModel, field_validator


class BaseModelWithId(BaseModel):
    id: str

    @field_validator("id", mode="before")
    @classmethod
    def id_to_str(cls, v):
        return str(v) if v is not None else v
