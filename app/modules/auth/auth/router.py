from app.modules.users.schemas.internal import UserInternal
from app.modules.users.schemas.responses import UserResponse
from app.modules.auth.auth.schemas.responses import CurrentSessionResponse, LoginResponse, SignUpCompleteResponse, VerifyEmailResponse
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.context import RequestContext
from app.core.database import get_session
from app.modules.auth.auth.schemas.requests import ChangeEmailRequest, ChangeEmailRequest, RequestEmailChangeRequest, SignUpRequest
from app.modules.auth.otp.schemas.requests import SendEmailVerificationOTPRequest
from app.shared.schemas import SingleObjectResponse
from app.modules.users.schemas import UserResponse
from app.shared.schemas.responses import SuccessResponse

from .dependencies import (
    get_auth_service,
    get_user_from_sign_up_complete_token,
    get_current_session,
    get_request_context,
)
from .docs import DOCSTRINGS, RESPONSES, SUMMARIES
from .schemas import (
    CurrentSessionResponse,
    LoginRequest,
    LoginResponse,
    RequestEmailVerificationResponse,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignUpCompleteRequest,
    SignUpCompleteResponse,
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
    response_model=SingleObjectResponse[CurrentSessionResponse],
    responses=RESPONSES.get("get_me", {}),
    summary=SUMMARIES.get("get_me", "Get current session"),
    description=DOCSTRINGS.get("get_me", ""),
)
async def me(
    current_session: CurrentSessionResponse = Depends(get_current_session),
) -> SingleObjectResponse[CurrentSessionResponse]:
    return SingleObjectResponse[CurrentSessionResponse](data=current_session)

# ---------------------------------------------------------------------
# POST
# ---------------------------------------------------------------------
@router.post(
    "/signup",
    response_model=SingleObjectResponse[UserResponse],
    responses=RESPONSES.get("signup", {}),
    summary=SUMMARIES.get("signup", "Sign up"),
    description=DOCSTRINGS.get("signup", ""),
)
async def signup(
    body: SignUpRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleObjectResponse[UserResponse]:
    data = await auth_service.sign_up(body, session)
    return SingleObjectResponse[UserResponse](data=data)


@router.post(
    "/signup/complete",
    response_model=SingleObjectResponse[SignUpCompleteResponse],
    responses=RESPONSES.get("sign_up_complete", {}),
    summary=SUMMARIES.get("sign_up_complete", "Complete sign up"),
    description=DOCSTRINGS.get("sign_up_complete", ""),
)
async def sign_up_complete(
    request: Request,
    response: Response,
    body: SignUpCompleteRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
    current_user: UserResponse = Depends(get_user_from_sign_up_complete_token),
) -> SingleObjectResponse[SignUpCompleteResponse]:
    data = await auth_service.sign_up_complete(current_user.email, body, session)
    response.delete_cookie("sign_up_complete_token")
    access_token = await auth_service.create_access_token(
        request, response, current_user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.user.id, set_cookie=True
    )
    return SingleObjectResponse[SignUpCompleteResponse](data=data)

@router.post(
    "/login",
    response_model=SingleObjectResponse[LoginResponse],
    responses=RESPONSES.get("login", {}),
    summary=SUMMARIES.get("login", "Login"),
    description=DOCSTRINGS.get("login", ""),
)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleObjectResponse[LoginResponse]:
    
    data = await auth_service.login(body, session)
    
    if not data.user.is_email_verified:
        return SingleObjectResponse[LoginResponse](data=data)
    
    if not data.user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, data.user.id, set_cookie=True
        )
        return SingleObjectResponse[LoginResponse](data=data)
    
    access_token = await auth_service.create_access_token(
        request, response, data.user.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.user.id, set_cookie=True
    )
    return SingleObjectResponse[LoginResponse](data=data)


@router.post(
    "/refresh",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=RESPONSES.get("refresh", {}),
    summary=SUMMARIES.get("refresh", "Refresh access token"),
    description=DOCSTRINGS.get("refresh", ""),
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    refresh_token = request.cookies.get("refresh_token")
    await auth_service.refresh(request, response, refresh_token, set_cookie=True)


@router.post(
    "/logout",
    response_model=SuccessResponse,
    responses=RESPONSES.get("logout", {}),
    summary=SUMMARIES.get("logout", "Logout"),
    description=DOCSTRINGS.get("logout", ""),
)
async def logout(
    response: Response,
) -> SuccessResponse:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return SuccessResponse(detail="Logged out successfully")


@router.post(
    "/request-email-verification",
    response_model=SuccessResponse,
    responses=RESPONSES.get("request_email_verification_otp", {}),
    summary=SUMMARIES.get("request_email_verification_otp", "Request email verification OTP"),
    description=DOCSTRINGS.get("request_email_verification_otp", ""),
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
    response_model=SingleObjectResponse[UserResponse],
    responses=RESPONSES.get("verify_email_otp", {}),
    summary=SUMMARIES.get("verify_email_otp", "Verify email OTP"),
    description=DOCSTRINGS.get("verify_email_otp", ""),
)
async def verify_email(
    body: VerifyEmailRequest,
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleObjectResponse[UserResponse]:
    user = await auth_service.verify_email(body, session)
    if not user.is_completed:
        sign_up_complete_token = await auth_service.create_sign_up_complete_token(
            request, response, user.id, set_cookie=True
        )
    return SingleObjectResponse[UserResponse](data=user)


@router.post(
    "/request-password-reset",
    response_model=SuccessResponse,
    responses=RESPONSES.get("request_password_reset_otp", {}),
    summary=SUMMARIES.get("request_password_reset_otp", "Request password reset link"),
    description=DOCSTRINGS.get("request_password_reset_otp", ""),
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
    responses=RESPONSES.get("reset_password", {}),
    summary=SUMMARIES.get("reset_password", "Reset password"),
    description=DOCSTRINGS.get("reset_password", ""),
)
async def reset_password(
    body: ResetPasswordRequest,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse:
    await auth_service.reset_password(body, session)
    return SuccessResponse(detail="Password reset successfully")


@router.post(
    "/request-email-change",
    response_model=SuccessResponse,
    responses=RESPONSES.get("request_email_change", {}),
    summary=SUMMARIES.get("request_email_change", "Request email change link"),
    description=DOCSTRINGS.get("request_email_change", ""),
)
async def request_email_change(
    body: RequestEmailChangeRequest,
    auth_service: AuthService = Depends(get_auth_service),
    ctx: RequestContext = Depends(get_request_context),
    session = Depends(get_session),
) -> SuccessResponse:
    await auth_service.request_email_change(body, ctx, session)
    return SuccessResponse(detail="Email change link sent successfully")


@router.post(
    "/confirm-email-change",
    response_model=SingleObjectResponse[UserResponse],
    responses=RESPONSES.get("confirm_email_change", {}),
    summary=SUMMARIES.get("confirm_email_change", "Confirm email change"),
    description=DOCSTRINGS.get("confirm_email_change", ""),
)
async def confirm_email_change(
    body: ChangeEmailRequest,
    request: Request,
    response: Response,
    session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> SingleObjectResponse[UserResponse]:
    data = await auth_service.confirm_email_change(body, session)
    access_token = await auth_service.create_access_token(
        request, response, data.id, set_cookie=True
    )
    refresh_token = await auth_service.create_refresh_token(
        request, response, data.id, set_cookie=True
    )
    return SingleObjectResponse[UserInternal](data=data)


@router.post(
    "/swaggerlogin",
    responses=RESPONSES.get("swaggerlogin", {}),
    summary=SUMMARIES.get("swaggerlogin", "Swagger login"),
    description=DOCSTRINGS.get("swaggerlogin", ""),
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
