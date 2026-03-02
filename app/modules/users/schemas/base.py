from pydantic import BaseModel, EmailStr

from app.core.enums import UserPlan
from app.shared.schemas.common import Link


class UserBase(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    whatsapp_number: str | None = None
    address: str | None = None
    plan: UserPlan | None = None
    logo: str | None = None
    business_name: str | None = None
    business_description: str | None = None
    store_url: str | None = None
    links: list[Link] | None = None
