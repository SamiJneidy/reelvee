from .base import OTPBase
from app.core.enums import OTPStatus
from pydantic import ConfigDict
from datetime import datetime

class OTPOut(OTPBase):
    code: str
    status: OTPStatus
    expires_at: datetime
    model_config = ConfigDict(from_attributes=True)
