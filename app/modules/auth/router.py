from app.modules.auth.schemas.responses import RefreshResponse, SwaggerLoginResponse
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import get_session
from app.modules.auth.exceptions import SignUpNotCompletedException
from app.modules.auth.schemas.requests import RefreshRequest, SignUpRequest, LogoutRequest
from app.modules.auth.otp.schemas.requests import SendEmailVerificationOTPRequest
from app.shared.schemas import SingleResponse
from app.modules.users.schemas import UserResponse
from app.shared.schemas.responses import SuccessResponse

from .dependencies import (
    get_auth_service,
    get_current_session,
)
from .docs import AuthDocs
from .schemas import (
    CurrentSessionResponse,
    LoginRequest,
    LoginResponse,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from .service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------
@router.get(
    "/me",
    response_model=SingleResponse[CurrentSessionResponse],
    summary=AuthDocs.GetMe.summary,
    description=AuthDocs.GetMe.description,
    responses=AuthDocs.GetMe.responses,
)
async def me(
    current_session: CurrentSessionResponse = Depends(get_current_session),
) -> SingleResponse[CurrentSessionResponse]:
    return SingleResponse[CurrentSessionResponse](data=current_session)

# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "/signup",
    response_model=SingleResponse[UserResponse],
    summary=AuthDocs.Signup.summary,
    description=AuthDocs.Signup.description,
    responses=AuthDocs.Signup.responses,
)
async def signup(
    body: SignUpRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponse[UserResponse]:
    data = await auth_service.sign_up(body, session)
    return SingleResponse[UserResponse](data=data)


@router.post(
    "/login",
    response_model=SingleResponse[LoginResponse],
    response_model_exclude_none=True,
    summary=AuthDocs.Login.summary,
    description=AuthDocs.Login.description,
    responses=AuthDocs.Login.responses,
)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponse[LoginResponse]:
    user = await auth_service.login(body, session)

    if not user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, user.id, set_cookie=False
        )
        return SingleResponse[LoginResponse](
            data=LoginResponse(user=user, sign_up_complete_token=sign_up_complete_token)
        )

    access_token = await auth_service.create_access_token(
        request, response, user.id, set_cookie=False
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, user.id, set_cookie=False
    )
    return SingleResponse[LoginResponse](
        data=LoginResponse(user=user, access_token=access_token, refresh_token=refresh_token)
    )


@router.post(
    "/refresh",
    response_model=SingleResponse[RefreshResponse],
    summary=AuthDocs.Refresh.summary,
    description=AuthDocs.Refresh.description,
    responses=AuthDocs.Refresh.responses,
)
async def refresh(
    request: Request,
    response: Response,
    body: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponse[RefreshResponse]:
    data = await auth_service.refresh(request, response, body.refresh_token, set_cookie=False)
    return SingleResponse[RefreshResponse](data=data)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary=AuthDocs.Logout.summary,
    description=AuthDocs.Logout.description,
)
async def logout(
    request: Request,
    response: Response,
    body: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.logout_session(request, response, body.refresh_token, delete_cookies=False)
    return SuccessResponse(detail="Logged out successfully")


@router.post(
    "/request-email-verification",
    response_model=SuccessResponse,
    summary=AuthDocs.RequestEmailVerification.summary,
    description=AuthDocs.RequestEmailVerification.description,
    responses=AuthDocs.RequestEmailVerification.responses,
)
async def request_email_verification(
    body: SendEmailVerificationOTPRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.request_email_verification(body, session)
    return SuccessResponse(detail="Email verification OTP sent successfully")

@router.post(
    "/verify-email",
    response_model=SingleResponse[VerifyEmailResponse],
    response_model_exclude_none=True,
    summary=AuthDocs.VerifyEmail.summary,
    description=AuthDocs.VerifyEmail.description,
    responses=AuthDocs.VerifyEmail.responses,
)
async def verify_email(
    body: VerifyEmailRequest,
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleResponse[VerifyEmailResponse]:
    user = await auth_service.verify_email(body, session)
    sign_up_complete_token = None
    if not user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, user.id, set_cookie=False
        )
    return SingleResponse[VerifyEmailResponse](
        data=VerifyEmailResponse(user=user, sign_up_complete_token=sign_up_complete_token)
    )


@router.post(
    "/request-password-reset",
    response_model=SuccessResponse,
    summary=AuthDocs.RequestPasswordReset.summary,
    description=AuthDocs.RequestPasswordReset.description,
    responses=AuthDocs.RequestPasswordReset.responses,
)
async def request_password_reset(
    body: RequestPasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.request_password_reset(body)
    return SuccessResponse(detail="Password reset link sent successfully")


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
    summary=AuthDocs.ResetPassword.summary,
    description=AuthDocs.ResetPassword.description,
    responses=AuthDocs.ResetPassword.responses,
)
async def reset_password(
    body: ResetPasswordRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.reset_password(body, session)
    return SuccessResponse(detail="Password reset successfully")


@router.post(
    "/swagger-login",
    summary=AuthDocs.SwaggerLogin.summary,
    description=AuthDocs.SwaggerLogin.description,
    responses=AuthDocs.SwaggerLogin.responses,
)
async def swagger_login(
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    login_credentials: OAuth2PasswordRequestForm = Depends(),
) -> SwaggerLoginResponse:
    login_data = LoginRequest(
        email=login_credentials.username,
        password=login_credentials.password,
    )
    user = await auth_service.login(login_data, session)
    if not user.is_completed:
        raise SignUpNotCompletedException()
    access_token = await auth_service.create_access_token(
        request, response, user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, user.id, set_cookie=True
    )
    return SwaggerLoginResponse(access_token=access_token, token_type="bearer")
