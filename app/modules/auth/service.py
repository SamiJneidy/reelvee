import uuid
from datetime import datetime, timezone
from beanie import PydanticObjectId
from fastapi import Request, Response

from app.core.config import settings
from app.core.enums import OTPUsage, UserStatus, TokenScope, UserStep
from app.core.security import hash_password, verify_password
from app.modules.auth.exceptions import (
    InvalidCredentialsException,
    PasswordResetNotAllowedException,
)
from app.modules.auth.schemas.requests import (
    LoginRequest,
    RequestPasswordResetRequest,
    SignUpRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.modules.auth.otp.exceptions import InvalidOTPException
from app.modules.auth.otp.schemas import SendEmailVerificationOTPRequest
from app.modules.auth.schemas.responses import (
    LoginResponse,
)
from app.modules.auth.otp.service import OTPService
from app.modules.auth.tokens.exceptions import InvalidTokenException
from app.modules.auth.tokens.schemas import AccessToken, PasswordResetToken, RefreshToken, RefreshTokenCreate, SignUpCompleteToken
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
from app.modules.users.service import UserService
from app.modules.users.schemas import UserCreate
from app.modules.auth.repository import AuthRepository
from app.shared.services import EmailService

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
            existing = await self._user_service.get_by_email_in_db(data.email)
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

    async def login(self, credentials: LoginRequest, session=None) -> LoginResponse:
        """Validate credentials and return user (caller sets cookies)."""
        
        user = await self._user_service.get_by_email_in_db(credentials.email)
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
        user = await self._user_service.get_by_email_in_db(data.email)
        if not user:
            raise UserNotFoundException()
        payload = PasswordResetToken(
            scope=TokenScope.RESET_PASSWORD,
            sub=str(user.id),
        )
        reset_token = self._token_service.generate_password_reset_token(payload)
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
        user = await self._user_service.get_by_email_in_db(data.email)
        if not user:
            raise UserNotFoundException()
        token_payload = self._token_service.decode_token(data.token)
        if token_payload.get("scope") != TokenScope.RESET_PASSWORD:
            raise PasswordResetNotAllowedException("Invalid Token")
        if token_payload.get("sub") != str(user.id):
            raise PasswordResetNotAllowedException("Invalid Token. Mismatch!")
        hashed = hash_password(data.new_password)
        await self._user_service.update_by_email(data.email, {"password": hashed}, session)
        await self._user_service.reset_invalid_login_attempts(data.email, session)
        await self._token_service.revoke_all_refresh_tokens_for_user(str(user.id))


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

    async def create_access_token(
        self, request: Request, response: Response, user_id: PydanticObjectId, set_cookie: bool = True
    ) -> str:
        payload = AccessToken(sub=str(user_id))
        token = self._token_service.generate_access_token(payload)
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
        self,
        request: Request,
        response: Response,
        user_id: PydanticObjectId,
        set_cookie: bool = True,
        family_id: str | None = None,
    ) -> str:
        payload = RefreshToken(sub=str(user_id), family_id=family_id or str(uuid.uuid4()))
        token = self._token_service.generate_refresh_token(payload)
        await self._token_service.create_refresh_token(
            RefreshTokenCreate(
                token_id=payload.jti,
                family_id=payload.family_id,
                user_id=str(user_id),
                expires_at=payload.exp,
            )
        )
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
        self, request: Request, response: Response, user_id: PydanticObjectId, set_cookie: bool = True
    ) -> str:
        payload = SignUpCompleteToken(sub=str(user_id))
        token = self._token_service.generate_sign_up_complete_token(payload)
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
        self, request: Request, response: Response, refresh_token: str, set_cookie: bool = True
    ) -> None:
        """Rotate refresh token and issue a new access token."""

        payload = self._token_service.decode_token(refresh_token)

        if payload.get("scope") != TokenScope.REFRESH:
            raise InvalidTokenException()

        jti = payload.get("jti")
        family_id = payload.get("family_id")
        user_id = PydanticObjectId(payload.get("sub"))

        if not jti or not family_id:
            raise InvalidTokenException()

        db_refresh_token = await self._token_service.get_refresh_token_by_jti(jti)

        if not db_refresh_token or db_refresh_token.is_revoked:
            await self._token_service.revoke_refresh_token_family(family_id)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            raise InvalidTokenException()

        # Invalidate the consumed token before issuing a new one
        await self._token_service.revoke_refresh_token(jti)

        await self.create_access_token(request, response, user_id, set_cookie)
        await self.create_refresh_token(request, response, user_id, set_cookie, family_id=family_id)

    async def logout_session(self, request: Request, response: Response) -> None:
        """Revoke the current refresh token family and clear cookies."""
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            try:
                payload = self._token_service.decode_token(refresh_token)
                family_id = payload.get("family_id")
                if family_id:
                    await self._token_service.revoke_refresh_token_family(family_id)
            except Exception:
                pass
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    async def get_user_from_token(self, token: str) -> UserInternal:
        """Resolve user from JWT."""
        payload = self._token_service.decode_token(token)
        user_id = PydanticObjectId(payload.get("sub"))
        return await self._user_service.get_by_id(user_id)
