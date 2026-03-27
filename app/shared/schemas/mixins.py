from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel


class TimeMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None

class TenantMixin(BaseModel):
    user_id: PydanticObjectId | None = None