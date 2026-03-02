from .base import OTPBase
from app.core.enums import OTPStatus
from beanie import PydanticObjectId
from datetime import datetime
from pydantic import ConfigDict

class OTPInternal(OTPBase):
    expires_at: datetime
    code: str
    status: OTPStatus

    model_config = ConfigDict(from_attributes=True)

class OTPInDB(OTPInternal):
    id: PydanticObjectId