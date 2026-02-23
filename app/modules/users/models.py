from datetime import datetime

from beanie import Document, Indexed

from app.core.enums import UserPlan, UserStatus, UserStep


class User(Document):
    """Single user table. Sign up with email + password only; rest filled in onboarding."""
    email: Indexed(str, unique=True)
    password: str

    # Profile (Sign Up Complete)
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
    links: list[str] | None = None
    qr_code: str | None = None

    # Sensetive data
    last_login: datetime | None = None
    invalid_login_attempts: int = 0
    status: UserStatus = UserStatus.PENDING
    step: UserStep = UserStep.ONE
    is_email_verified: bool = False
    is_completed: bool = False

    class Settings:
        name = "users"
