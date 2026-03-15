from datetime import datetime
from pydantic import BaseModel


class TimeMixin(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
