from datetime import datetime
from pydantic import BaseModel, EmailStr
from .base import OTPBase

class OTPCreate(OTPBase):
    expires_at: datetime

class SendEmailVerificationOTPRequest(BaseModel):
    email: EmailStr