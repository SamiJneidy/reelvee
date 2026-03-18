from app.modules.users.schemas.responses import UserResponse
from app.modules.auth.schemas.responses import CurrentSessionResponse, LoginResponse, VerifyEmailResponse
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.context import CurrentUser
from app.core.database import get_session
from app.modules.auth.schemas.requests import SignUpRequest
from app.modules.auth.otp.schemas.requests import SendEmailVerificationOTPRequest
from app.shared.schemas import SingleResponse
from app.modules.users.schemas import UserResponse
from app.shared.schemas.responses import SuccessResponse

from .dependencies import (
    get_auth_service,
    get_user_from_sign_up_complete_token,
    get_current_session,
    get_request_context,
)
from .docs import AuthDocs
from .schemas import (
    CurrentSessionResponse,
    LoginRequest,
    LoginResponse,
    RequestEmailVerificationResponse,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
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
    data = await auth_service.login(body, session)
    
    if not data.user.is_email_verified:
        return SingleResponse[LoginResponse](data=data)
    
    if not data.user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, data.user.id, set_cookie=True
        )
        return SingleResponse[LoginResponse](data=data)
    
    access_token = await auth_service.create_access_token(
        request, response, data.user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.user.id, set_cookie=True
    )
    return SingleResponse[LoginResponse](data=data)


@router.post(
    "/refresh",
    response_model=SuccessResponse,
    summary=AuthDocs.Refresh.summary,
    description=AuthDocs.Refresh.description,
    responses=AuthDocs.Refresh.responses,
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    refresh_token = request.cookies.get("refresh_token")
    await auth_service.refresh(request, response, refresh_token, set_cookie=True)
    return SuccessResponse(detail="Access token refreshed successfully")


@router.post(
    "/logout",
    response_model=SuccessResponse,
    summary=AuthDocs.Logout.summary,
    description=AuthDocs.Logout.description,
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.logout_session(request, response)
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
    response_model=SingleResponse[UserResponse],
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
) -> SingleResponse[UserResponse]:
    user = await auth_service.verify_email(body, session)
    if not user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, user.id, set_cookie=True
        )
    return SingleResponse[UserResponse](data=user)


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
    "/swaggerlogin",
    summary=AuthDocs.SwaggerLogin.summary,
    description=AuthDocs.SwaggerLogin.description,
    responses=AuthDocs.SwaggerLogin.responses,
)
async def swaggerlogin(
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    login_credentials: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    login_data = LoginRequest(
        email=login_credentials.username,
        password=login_credentials.password,
    )
    login_response = await auth_service.login(login_data, session)
    access_token = await auth_service.create_access_token(
        request, response, login_response.user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, login_response.user.id, set_cookie=True
    )
    return {"access_token": access_token, "token_type": "bearer"}
