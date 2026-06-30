from typing import Annotated
from urllib.parse import urlencode

import structlog
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from app.core.audit import service as audit
from app.core.audit.enums import AuditEventType
from app.core.config import settings
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.google.dependencies import get_google_auth_service
from app.modules.auth.google.exceptions import (
    GoogleOAuthException,
    GoogleOAuthNotConfiguredException,
)
from app.modules.auth.google.schemas import ExchangeGoogleAuthTokenRequest, ExchangeGoogleAuthTokenResponse
from app.modules.auth.google.service import GoogleAuthService
from app.modules.auth.service import AuthService
from app.modules.auth.tokens.dependencies import get_token_service
from app.modules.auth.tokens.schemas import GoogleAuthToken
from app.modules.auth.tokens.service import TokenService
from app.shared.schemas.responses import SingleResponse

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/google", tags=["Google OAuth"])

def _frontend_callback_url() -> str:
    frontend_url = settings.frontend_url_dev if settings.frontend_environment == "DEVELOPMENT" else settings.frontend_url
    return f"{frontend_url}{settings.frontend_callback_path}"

def _frontend_base_url() -> str:
    return settings.frontend_url_dev if settings.frontend_environment == "DEVELOPMENT" else settings.frontend_url

def _error_redirect(message: str) -> RedirectResponse:
    params = urlencode({"error": message})
    return RedirectResponse(url=f"{_frontend_base_url()}/login?{params}")


@router.get("/login", summary="Redirect to Google consent screen")
async def google_login(
    google_auth_service: Annotated[GoogleAuthService, Depends(get_google_auth_service)],
) -> RedirectResponse:
    state = GoogleAuthService.generate_state()
    auth_url = google_auth_service.get_authorization_url(state)
    redirect = RedirectResponse(url=auth_url)
    redirect.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        max_age=300,
        samesite="lax",
    )
    return redirect


@router.get("/callback", include_in_schema=False)
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service),
    token_service: TokenService = Depends(get_token_service),
) -> RedirectResponse:
    if error:
        return _error_redirect(error)

    if not code or not state:
        return _error_redirect("missing_code_or_state")

    # CSRF — verify the state cookie matches the state param
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        return _error_redirect("invalid_state")

    try:
        tokens = await google_auth_service.exchange_code(code)
        user_info = await google_auth_service.get_user_info(tokens.access_token)
        user = await google_auth_service.get_or_create_user(user_info)
    except (GoogleOAuthException, GoogleOAuthNotConfiguredException) as exc:
        logger.warning("google_oauth_callback_error", error=str(exc))
        return _error_redirect("auth_failed")
    except Exception as exc:
        logger.error("google_oauth_unexpected_error", error=str(exc))
        return _error_redirect("unexpected_error")

    await audit.log_event(
        AuditEventType.AUTH_GOOGLE_LOGIN,
        user_id=user.id,
        details={"email": user_info.email},
    )

    # Issue a short-lived google_auth_token. The frontend will POST it back to
    # /exchange to receive real session cookies — this avoids setting cross-origin
    # cookies directly from the redirect response.
    google_auth_token = token_service.generate_google_auth_token(GoogleAuthToken(sub=str(user.id), email=user.email))
    params = urlencode({"google_auth_token": google_auth_token})
    redirect_response = RedirectResponse(url=f"{_frontend_callback_url()}?{params}")
    redirect_response.delete_cookie("oauth_state")
    return redirect_response


@router.post("/exchange", summary="Exchange Google auth token for session tokens")
async def exchange_google_auth_token(
    request: Request,
    response: Response,
    body: ExchangeGoogleAuthTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponse[ExchangeGoogleAuthTokenResponse]:
    user = await auth_service.complete_google_login(body.google_auth_token)
    access_token = None
    if user.is_completed:
        access_token = await auth_service.create_access_token(request, response, user.id, set_cookie=False)
        refresh_token = await auth_service.create_refresh_token(request, response, user.id)
        redirect_to = "dashboard"
    else:
        await auth_service.create_sign_up_complete_token(request, response, user.id)
        redirect_to = "user-onboarding"

    return SingleResponse(
        data=ExchangeGoogleAuthTokenResponse(
            redirect_to=redirect_to,
            user=user,
            access_token=access_token,
        )
    )