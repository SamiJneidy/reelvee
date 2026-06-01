from pydantic import BaseModel
from pydantic import ConfigDict


class File(BaseModel):
    id: str
    key: str
    url: str
    model_config = ConfigDict(from_attributes=True)