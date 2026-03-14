from fastapi import Depends, HTTPException, Request, status
from typing import Annotated

from app.core.context import RequestContext
from app.modules.auth.auth.schemas.responses import CurrentSessionResponse
from app.modules.auth.auth.service import AuthService
from app.modules.auth.auth.repository import AuthRepository
from app.modules.auth.otp.depenencies import OTPService, get_otp_service
from app.modules.auth.tokens.dependencies import TokenService, get_token_service
from app.modules.users.dependencies import UserService, get_user_service
from app.modules.users.schemas import UserResponse
from app.shared.dependencies.email import EmailService, get_email_service


def get_auth_repository() -> AuthRepository:
    return AuthRepository()


def get_auth_service(
    auth_repo: Annotated[AuthRepository, Depends(get_auth_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    otp_service: Annotated[OTPService, Depends(get_otp_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> AuthService:
    """Returns authentication service dependency."""
    return AuthService(
        auth_repo=auth_repo,
        user_service=user_service,
        token_service=token_service,
        otp_service=otp_service,
        email_service=email_service,
    )


async def get_current_session(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CurrentSessionResponse:
    """Load current session from access_token cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token was not found in cookies")
    user = await auth_service.get_user_from_token(token)
    return CurrentSessionResponse(user=UserResponse.model_validate(user))


async def get_request_context(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> RequestContext:
    """Get request context."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token was not found in cookies")
    user = await auth_service.get_user_from_token(token)
    return RequestContext(user=user)


async def get_user_from_sign_up_complete_token(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Resolve user from JWT sign_up_complete_token."""
    token = request.cookies.get("sign_up_complete_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token was not found in cookies")
    user = await auth_service.get_user_from_token(token)
    return UserResponse.model_validate(user)