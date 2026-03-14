from pydantic import BaseModel


class File(BaseModel):
    id: str
    key: str
    url: str
