from pydantic import BaseModel
from datetime import datetime
from app.core.enums import TokenScope
from typing import Optional, Literal

class TokenPayloadBase(BaseModel):
    scope: TokenScope
    sub: str
    iat: datetime
    exp: datetime

class AccessToken(TokenPayloadBase):
    scope: Literal[TokenScope.ACCESS]

class RefreshToken(TokenPayloadBase):
    scope: Literal[TokenScope.REFRESH]

class SignUpCompleteToken(TokenPayloadBase):
    scope: Literal[TokenScope.SIGN_UP_COMPLETE]

class PasswordResetToken(TokenPayloadBase):
    scope: Literal[TokenScope.RESET_PASSWORD]
