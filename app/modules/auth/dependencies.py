from fastapi import Depends
from typing import Annotated

from app.core.enums import TokenScope
from app.core.security import oauth2_scheme
from app.core.context import CurrentUser
from app.modules.auth.schemas.responses import CurrentSessionResponse
from app.modules.auth.service import AuthService
from app.modules.auth.repository import AuthRepository
from app.modules.auth.otp.dependencies import OTPService, get_otp_service
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
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CurrentSessionResponse:
    """Load current session from Authorization: Bearer access token."""
    user = await auth_service.get_user_from_token(token, required_scope=TokenScope.ACCESS)
    return CurrentSessionResponse(user=UserResponse.model_validate(user))


async def get_request_context(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CurrentUser:
    """Resolve current user from Authorization: Bearer access token."""
    user = await auth_service.get_user_from_token(token, required_scope=TokenScope.ACCESS)
    return CurrentUser(user=user)


async def get_user_from_sign_up_complete_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Resolve user from Authorization: Bearer sign_up_complete token."""
    user = await auth_service.get_user_from_token(token, required_scope=TokenScope.SIGN_UP_COMPLETE)
    return UserResponse.model_validate(user)
