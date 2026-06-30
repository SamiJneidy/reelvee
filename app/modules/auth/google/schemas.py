from typing import Literal
from pydantic import BaseModel, Field

from app.modules.users.schemas.responses import UserResponse


class GoogleAuthorizationParams(BaseModel):
    """Parameters sent to Google to build the authorization URL."""
    client_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: str = "openid email profile"
    state: str
    access_type: str = "offline"
    prompt: str = "select_account"


class GoogleTokenRequest(BaseModel):
    """Body sent to Google token endpoint to exchange an authorization code."""
    client_id: str
    client_secret: str
    code: str
    grant_type: str = "authorization_code"
    redirect_uri: str


class GoogleTokenResponse(BaseModel):
    """Response from Google token endpoint."""
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    id_token: str | None = None
    refresh_token: str | None = None


class GoogleUserInfo(BaseModel):
    """Subset of fields returned by Google userinfo endpoint we actually use."""
    sub: str = Field(..., description="Unique Google user ID")
    email: str
    email_verified: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    name: str | None = None

class ExchangeGoogleAuthTokenRequest(BaseModel):
    google_auth_token: str

class ExchangeGoogleAuthTokenResponse(BaseModel):
    redirect_to: Literal["dashboard", "user-onboarding"]
    user: UserResponse
    access_token: str | None = None