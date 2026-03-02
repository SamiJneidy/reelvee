from datetime import datetime, timedelta, timezone
from fastapi import Request, Response

from app.core.config import settings
from app.core.context import RequestContext
from app.core.enums import OTPStatus, OTPUsage, UserStatus, TokenScope, UserStep
from app.core.security import hash_password, verify_password
from app.modules.auth.auth.exceptions import (
    DuplicateKeyErrorException,
    EmailChangeNotAllowedException,
    InvalidCredentialsException,
    PasswordResetNotAllowedException,
    UserAlreadyCompletedException,
)
from app.modules.auth.auth.schemas.requests import (
    ChangeEmailRequest,
    LoginRequest,
    ChangeEmailRequest,
    RequestEmailChangeRequest,
    RequestPasswordResetRequest,
    SignUpCompleteRequest,
    SignUpRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.modules.auth.otp.exceptions import InvalidOTPException
from app.modules.auth.otp.schemas import SendEmailVerificationOTPRequest
from app.modules.auth.auth.schemas.responses import (
    LoginResponse,
    RequestEmailVerificationResponse,
    ResetPasswordResponse,
    SignUpCompleteResponse,  
    VerifyEmailResponse,
)
from app.modules.auth.otp.service import OTPService
from app.modules.auth.tokens.schemas import AccessToken, EmailChangeToken, PasswordResetToken, RefreshToken, SignUpCompleteToken
from app.modules.auth.tokens.service import TokenService
from app.modules.users.exceptions import (
    UserAlreadyExistsException,
    UserBlockedException,
    UserDisabledException,
    UserNotActiveException,
    UserNotFoundException,
    UserNotVerifiedException,
)
from app.modules.users.schemas import UserResponse
from app.modules.users.schemas.internal import UserInternal
from app.modules.users.schemas.internal import UserUpdateInternal
from app.modules.users.service import UserService
from app.modules.users.schemas import UserCreate
from pymongo.errors import DuplicateKeyError
from app.modules.auth.auth.repository import AuthRepository
from app.shared.services.email_service import EmailService

class AuthService:

    def __init__(
        self,
        auth_repo: AuthRepository,
        user_service: UserService,
        token_service: TokenService,
        email_service: EmailService,
        otp_service: OTPService,
    ) -> None:
        self._auth_repo = auth_repo
        self._user_service = user_service
        self._token_service = token_service
        self._email_service = email_service
        self._otp_service = otp_service

    async def sign_up(self, data: SignUpRequest, session=None) -> UserResponse:
        try:
            existing = await self._user_service.get_user_in_db(data.email)
            if existing:
                raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass

        user_data = UserCreate(
            email=data.email,
            password=hash_password(data.password),
            status=UserStatus.PENDING,
            step=UserStep.ONE,
            is_email_verified=False,
            is_completed=False,
            is_deleted=False,
            last_login=None,
            invalid_login_attempts=0,
            links=[],
        )

        user = await self._user_service.create_user(user_data, session)
        otp_req = SendEmailVerificationOTPRequest(email=data.email)
        await self._otp_service.create_email_verification_otp(otp_req, session)
        return UserResponse.model_validate(user)

    async def sign_up_complete(
        self, email: str, data: SignUpCompleteRequest, session = None
    ) -> SignUpCompleteResponse:
        user = await self._user_service.get_by_email(email)
        if not user.is_email_verified:
            raise UserNotVerifiedException()
        if user.is_completed:
            raise UserAlreadyCompletedException()
        user_data = UserUpdateInternal(
            **data.model_dump(),
            status=UserStatus.ACTIVE,
            step=UserStep.TWO,
            is_completed=True,
            is_deleted=False,
            last_login=datetime.now(timezone.utc),
            invalid_login_attempts=0,
        )
        try:
            full_user = await self._user_service.update_by_email(email, user_data, session)
        except DuplicateKeyError:
            raise DuplicateKeyErrorException("The store link or whatsapp number is already in use")
        return SignUpCompleteResponse(user=UserResponse.model_validate(full_user))

    async def login(self, credentials: LoginRequest, session=None) -> LoginResponse:
        """Validate credentials and return user (caller sets cookies)."""
        
        user = await self._user_service.get_user_in_db(credentials.email)
        if not verify_password(credentials.password, user.password):
            await self._user_service.increment_invalid_login_attempts(credentials.email, session)
            raise InvalidCredentialsException()

        if not user.is_email_verified:
            email_verification_req = SendEmailVerificationOTPRequest(email=credentials.email)
            await self.request_email_verification(email_verification_req, session)
            return LoginResponse(user=UserResponse.model_validate(user))

        if not user.is_completed:
            # ISSUE SIGN UP COMPLETE TOKEN IN THE ROUTER
            return LoginResponse(user=UserResponse.model_validate(user))

        if user.status == UserStatus.DISABLED:
            raise UserDisabledException()
        if user.status == UserStatus.BLOCKED:
            raise UserBlockedException()
        if user.status == UserStatus.PENDING:
            raise UserNotVerifiedException()
        if user.status != UserStatus.ACTIVE:
            raise UserNotActiveException()

        if user.invalid_login_attempts > 0:
            await self._user_service.reset_invalid_login_attempts(credentials.email, session)
        
        user = await self._user_service.update_last_login(credentials.email, datetime.now(timezone.utc), session)
        return LoginResponse(user=UserResponse.model_validate(user))

    async def request_password_reset(
        self, data: RequestPasswordResetRequest, session = None
    ) -> None:
        """Create and send password reset link."""
        user = await self._user_service.get_user_in_db(data.email)
        if not user:
            raise UserNotFoundException()
        payload = PasswordResetToken(
            scope=TokenScope.RESET_PASSWORD,
            sub=user.id,
        )
        reset_token = self._token_service.create_password_reset_token(payload)
        reset_url = f"{settings.frontend_url}/reset-password?email={data.email}&token={reset_token}"
        await self._email_service.send_password_reset_link(data.email, reset_url)

    async def request_email_verification(
        self, data: SendEmailVerificationOTPRequest, session = None
    ) -> None:
        await self._otp_service.create_email_verification_otp(data, session)
    

    async def reset_password(
        self, data: ResetPasswordRequest, session = None
    ) -> None:
        """Reset password. Requires a password reset token."""
        user = await self._user_service.get_user_in_db(data.email)
        if not user:
            raise UserNotFoundException()
        token_payload = self._token_service.decode_token(data.token)
        if token_payload.get("scope") != TokenScope.RESET_PASSWORD:
            raise PasswordResetNotAllowedException("Invalid Token")
        if token_payload.get("sub") != user.id:
            raise PasswordResetNotAllowedException("Invalid Token. Mismatch!")
        hashed = hash_password(data.new_password)
        await self._user_service.update_by_email(data.email, {"password": hashed}, session)
        await self._user_service.reset_invalid_login_attempts(data.email, session)


    async def verify_email(
        self, data: VerifyEmailRequest, session=None
    ) -> UserInternal:
        otp = await self._otp_service.get_otp(email=data.email, code=data.code, usage=OTPUsage.EMAIL_VERIFICATION)
        if otp.usage != OTPUsage.EMAIL_VERIFICATION or otp.email != data.email:
            raise InvalidOTPException()
        user = await self._user_service.get_by_email(data.email)
        if not user.is_email_verified:
            user =await self._user_service.update_by_email(data.email, {"is_email_verified": True}, session)
        await self._otp_service.verify_otp(data.code, session)
        return UserInternal.model_validate(user)

    async def request_email_change(
        self, data: RequestEmailChangeRequest, ctx: RequestContext, session = None
    ) -> None:
        if not verify_password(data.password, ctx.user.password):
            raise InvalidCredentialsException()
        payload = EmailChangeToken(
            scope=TokenScope.EMAIL_CHANGE,
            sub=ctx.user.id,
            current_email=ctx.user.email,
            new_email=data.new_email,
        )
        change_token = self._token_service.create_email_change_token(payload)
        change_url = f"{settings.frontend_url}/change-email?token={change_token}"
        await self._email_service.send_email_change_link(data.new_email, change_url)

    async def confirm_email_change(
        self, data: ChangeEmailRequest, session = None
    ) -> UserInternal:
        token_payload = self._token_service.decode_token(data.token)
        token = EmailChangeToken.model_validate(token_payload)
        if token.scope != TokenScope.EMAIL_CHANGE:
            raise EmailChangeNotAllowedException("Invalid Token")
        user = await self._user_service.get_by_id(token.sub)
        if user.email != token.current_email:
            raise EmailChangeNotAllowedException("Invalid Token. Mismatch!")
        updated_user = await self._user_service.update_by_email(token.current_email, {"email": token.new_email}, session)
        return UserInternal.model_validate(updated_user)

    async def create_access_token(
        self, request: Request, response: Response, user_id: str, set_cookie: bool = True
    ) -> str:
        """Create access token. user_id is string (Beanie id)."""
        payload = AccessToken(sub=user_id)
        token = self._token_service.create_access_token(payload)
        if set_cookie:
            await self.set_access_token_cookie(request, response, token)
        return token

    async def set_access_token_cookie(
        self, request: Request, response: Response, token: str
    ) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.access_token_expiration_minutes * 60,
            path="/"
        )
    
    async def create_refresh_token(
        self, request: Request, response: Response, user_id: str, set_cookie: bool = True
    ) -> str:
        payload = RefreshToken(sub=user_id)
        token = self._token_service.create_refresh_token(payload)
        if set_cookie:
            await self.set_refresh_token_cookie(request, response, token)
        return token

    async def set_refresh_token_cookie(
        self, request: Request, response: Response, token: str
    ) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.refresh_token_expiration_days * 24 * 60 * 60,
            path="/"
        )
        return token

    async def create_sign_up_complete_token(
        self, request: Request, response: Response, user_id: str, set_cookie: bool = True
    ) -> str:
        payload = SignUpCompleteToken(sub=user_id)
        token = self._token_service.create_sign_up_complete_token(payload)
        if set_cookie:
            await self.set_sign_up_complete_token_cookie(request, response, token)
        return token

    async def set_sign_up_complete_token_cookie(
        self, request: Request, response: Response, token: str
    ) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="sign_up_complete_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.sign_up_complete_expiration_days * 24 * 60 * 60,
            path="/"
        )
        return token

    async def refresh(
        self, request: Request, response: Response, refresh_token: str, set_cookie: bool = False
    ) -> None:
        """Issue new access token from refresh token."""
        payload = self._token_service.decode_token(refresh_token)
        user_id = payload.get("sub")
        await self.create_access_token(request, response, user_id, set_cookie)

    async def get_user_from_token(self, token: str) -> UserInternal:
        """Resolve user from JWT."""
        payload = self._token_service.decode_token(token)
        user_id = payload.get("sub")
        return await self._user_service.get_by_id(user_id)
