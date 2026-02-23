from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.core.enums import OTPUsage

class OTPBase(BaseModel):
    email: EmailStr
    usage: OTPUsage