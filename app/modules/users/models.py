from datetime import datetime
from beanie import Indexed

from app.core.enums import UserPlan, UserStatus, UserStep
from app.shared.models.base import BaseDocument


class User(BaseDocument):
    """Account + personal profile. Store customization lives in the stores collection."""
    email: Indexed(str, unique=True)
    password: str

    # Personal profile (completed during onboarding)
    first_name: str | None = None
    last_name: str | None = None
    country_code: str | None = None
    whatsapp_number: str | None = Indexed(str, unique=True)
    address: str | None = None
    currency: str | None = None
    plan: UserPlan | None = None

    # Security
    last_login: datetime | None = None
    invalid_login_attempts: int = 0
    status: UserStatus = UserStatus.PENDING
    step: UserStep = UserStep.ONE
    is_email_verified: bool = False
    is_completed: bool = False
    is_deleted: bool = False

    class Settings:
        name = "users"
