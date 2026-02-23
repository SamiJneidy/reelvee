from beanie import Document, Indexed
from datetime import datetime
from app.core.enums import OTPUsage, OTPStatus

class OTP(Document):
    email: Indexed(str)
    code: Indexed(str)
    usage: Indexed(OTPUsage)
    status: Indexed(OTPStatus)
    expires_at: datetime

    class Settings:
        name = "otps"
        indexes = [
            [
                ("email", 1),
                ("code", 1),
                {"unique": True}
            ]
        ]