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
from app.modules.auth.google.service import GoogleAuthService
from app.modules.auth.service import AuthService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/google", tags=["Google OAuth"])

FRONTEND_CALLBACK_PATH = "/auth/google/callback"

def _frontend_callback_url() -> str:
    return f"{settings.frontend_url}{FRONTEND_CALLBACK_PATH}"

def _error_redirect(message: str) -> RedirectResponse:
    params = urlencode({"error": message})
    return RedirectResponse(url=f"{settings.frontend_url}/login?{params}")


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
    response: Response,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    auth_service: AuthService = Depends(get_auth_service),
    google_auth_service: GoogleAuthService = Depends(get_google_auth_service),
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

    # Build the redirect first, then set cookies directly on it.
    # Cookies set on the injected Response parameter are NOT transferred to an
    # explicitly returned RedirectResponse — they must be set on the object returned.
    if user.is_completed:
        redirect_to_page = "dashboard"
        token = await auth_service.create_refresh_token(
            request, response, user.id, set_cookie=False
        )
        params = urlencode({"redirect_to": redirect_to_page})
        redirect_response = RedirectResponse(url=f"{_frontend_callback_url()}?{params}")
        await auth_service.set_refresh_token_cookie(request, redirect_response, token)
    else:
        redirect_to_page = "user-onboarding"
        token = await auth_service.create_sign_up_complete_token(
            request, response, user.id, set_cookie=False
        )
        params = urlencode({"redirect_to": redirect_to_page})
        redirect_response = RedirectResponse(url=f"{_frontend_callback_url()}?{params}")
        await auth_service.set_sign_up_complete_token_cookie(request, redirect_response, token)

    redirect_response.delete_cookie("oauth_state")
    return redirect_response
