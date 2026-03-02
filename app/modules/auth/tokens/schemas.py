from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from app.core.enums import TokenScope
from typing import Optional, Literal
from app.core.config import settings

class TokenPayloadBase(BaseModel):
    scope: TokenScope
    sub: str
    iat: datetime
    exp: datetime

class AccessToken(TokenPayloadBase):
    scope: Literal[TokenScope.ACCESS] = TokenScope.ACCESS
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expiration_minutes)

class RefreshToken(TokenPayloadBase):
    scope: Literal[TokenScope.REFRESH] = TokenScope.REFRESH
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expiration_days)

class SignUpCompleteToken(TokenPayloadBase):
    scope: Literal[TokenScope.SIGN_UP_COMPLETE] = TokenScope.SIGN_UP_COMPLETE
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime = datetime.now(timezone.utc) + timedelta(days=settings.sign_up_complete_expiration_days)

class PasswordResetToken(TokenPayloadBase):
    scope: Literal[TokenScope.RESET_PASSWORD] = TokenScope.RESET_PASSWORD
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_expiration_minutes)

class EmailChangeToken(TokenPayloadBase):
    scope: Literal[TokenScope.EMAIL_CHANGE] = TokenScope.EMAIL_CHANGE
    new_email: EmailStr
    current_email: EmailStr
    iat: datetime = datetime.now(timezone.utc)
    exp: datetime = datetime.now(timezone.utc) + timedelta(minutes=settings.email_change_token_expiration_minutes)