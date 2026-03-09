from beanie import Document, Indexed
from pymongo import IndexModel
from datetime import datetime
from app.core.enums import OTPUsage, OTPStatus
from app.shared.models.mixins import BaseDocument

class OTP(BaseDocument):
    email: Indexed(str)
    code: Indexed(str)
    usage: Indexed(str)
    status: Indexed(str)
    expires_at: datetime

    class Settings:
        name = "otps"
        indexes = [
            IndexModel(
                [("email", 1), ("code", 1)],
                unique = True,
            )
        ]