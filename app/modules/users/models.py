from datetime import datetime

from pydantic import BaseModel
from beanie import Document, Indexed

from app.core.enums import UserPlan, UserStatus, UserStep
from app.shared.schemas.common import Link
from app.shared.models.base import BaseDocument

class User(BaseDocument):
    """Single user table. Sign up with email + password only; rest filled in onboarding."""
    email: Indexed(str, unique=True)
    password: str

    # Profile (Sign Up Complete)
    first_name: str | None
    last_name: str | None
    country_code: str | None
    whatsapp_number: str | None = Indexed(str, unique=True)
    address: str | None
    plan: UserPlan | None
    logo: str | None
    business_name: str | None
    business_description: str | None
    store_url: str | None = Indexed(str, unique=True)
    links: list[Link]
    qr_code: str | None

    # Sensetive data    
    last_login: datetime | None
    invalid_login_attempts: int
    status: UserStatus
    step: UserStep
    is_email_verified: bool
    is_completed: bool
    is_deleted: bool

    class Settings:
        name = "users"
