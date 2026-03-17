from pydantic import BaseModel
from beanie import PydanticObjectId

class BaseModelWithId(BaseModel):
    id: PydanticObjectId
