from pydantic import BaseModel
from app.core.enums import UserStatus


class UserFilters(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    email: str | None = None
    whatsapp_number: str | None = None
    status: UserStatus | None = None
