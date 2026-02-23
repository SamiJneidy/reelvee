from .base import OTPBase
from app.core.enums import OTPStatus
from beanie import PydanticObjectId
from datetime import datetime

class OTPInternal(OTPBase):
    expires_at: datetime
    code: str
    status: OTPStatus

class OTPInDB(OTPInternal):
    id: PydanticObjectId