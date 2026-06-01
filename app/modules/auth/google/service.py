import secrets
from urllib.parse import urlencode

import httpx
import structlog

from app.core.audit import service as audit
from app.core.audit.enums import AuditEventType
from app.core.config import settings
from app.core.enums import AuthProvider, UserStatus, UserStep
from app.modules.auth.google.exceptions import (
    GoogleOAuthException,
    GoogleOAuthNotConfiguredException,
)
from app.modules.auth.google.schemas import (
    GoogleAuthorizationParams,
    GoogleTokenRequest,
    GoogleTokenResponse,
    GoogleUserInfo,
)
from app.modules.users.exceptions import UserNotFoundException
from app.modules.users.schemas import UserCreate
from app.modules.users.schemas.internal import UserInternal
from app.modules.users.service import UserService

logger = structlog.get_logger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleAuthService:

    def __init__(self, user_service: UserService) -> None:
        self._user_service = user_service

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    def get_authorization_url(self, state: str) -> str:
        if not settings.google_client_id or not settings.google_redirect_uri:
            raise GoogleOAuthNotConfiguredException()
        params = GoogleAuthorizationParams(
            client_id=settings.google_client_id,
            redirect_uri=settings.google_redirect_uri,
            state=state,
        )
        return f"{GOOGLE_AUTH_URL}?{urlencode(params.model_dump())}"

    # ------------------------------------------------------------------
    # Token exchange
    # ------------------------------------------------------------------

    async def exchange_code(self, code: str) -> GoogleTokenResponse:
        if not settings.google_client_id or not settings.google_client_secret or not settings.google_redirect_uri:
            raise GoogleOAuthNotConfiguredException()
        body = GoogleTokenRequest(
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            code=code,
            redirect_uri=settings.google_redirect_uri,
        )
        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=body.model_dump())
        if response.status_code != 200:
            logger.warning("google_token_exchange_failed", status=response.status_code, body=response.text)
            raise GoogleOAuthException()
        return GoogleTokenResponse.model_validate(response.json())

    async def get_user_info(self, access_token: str) -> GoogleUserInfo:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code != 200:
            logger.warning("google_userinfo_failed", status=response.status_code)
            raise GoogleOAuthException()
        return GoogleUserInfo.model_validate(response.json())

    # ------------------------------------------------------------------
    # User lookup / provisioning
    # ------------------------------------------------------------------

    async def get_or_create_user(self, user_info: GoogleUserInfo) -> UserInternal:
        """Return existing user or create a new one; link google_id when missing."""
        try:
            user = await self._user_service.get_by_email(user_info.email)
            if not user.google_id:
                user = await self._user_service.update_by_email(
                    user_info.email,
                    {
                        "google_id": user_info.sub,
                        "auth_provider": AuthProvider.GOOGLE,
                        "is_email_verified": True,
                    },
                )
            return user
        except UserNotFoundException:
            pass

        user_data = UserCreate(
            email=user_info.email,
            password=None,
            google_id=user_info.sub,
            auth_provider=AuthProvider.GOOGLE,
            first_name=user_info.given_name,
            last_name=user_info.family_name,
            status=UserStatus.PENDING,
            step=UserStep.ONE,
            is_email_verified=True,
            is_completed=False,
            is_deleted=False,
            last_login=None,
            invalid_login_attempts=0,
        )
        user = await self._user_service.create_user(user_data)
        await audit.log_event(
            AuditEventType.AUTH_SIGNUP,
            user_id=user.id,
            details={"email": user_info.email, "provider": "google"},
        )
        return user
