from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.enums import OTPStatus, OTPUsage
from app.core.config import settings
from .repository import OTPRepository
from app.shared.utils.random_helper import generate_random_code
from .schemas import (
    OTPCreate, 
    OTPInternal,
    SendEmailVerificationOTPRequest,
)
from .exceptions import (
    OTPExpiredException,
    InvalidOTPException,
    OTPAlreadyUsedException,
    SuspiciousOTPActivityException,
)
from app.shared.email.service import EmailService

class OTPService:
    def __init__(self, otp_repo: OTPRepository, email_service: EmailService) -> None:
        self.otp_repo = otp_repo
        self.email_service = email_service

    async def get_otp(
        self,
        code: Optional[str] = None,
        email: Optional[str] = None,
        usage: Optional[OTPUsage] = None,
        session = None,
    ) -> OTPInternal:
        otp = await self.otp_repo.get_otp(email=email, usage=usage, code=code, session=session)
        if not otp:
            raise InvalidOTPException()
        return OTPInternal.model_validate(otp)

    async def create_email_verification_otp(
        self, data: SendEmailVerificationOTPRequest, session = None
    ) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.email_verification_otp_expiration_minutes)
        otp_data = OTPCreate(
            email=data.email,
            usage=OTPUsage.EMAIL_VERIFICATION,
            expires_at=expires_at,
        )
        otp = await self._create_otp(otp_data, session=session)
        await self.email_service.send_email_verification_otp(data.email, otp.code)


    async def _create_otp(self, data: OTPCreate, session = None) -> OTPInternal:
        await self.otp_repo.revoke_otps(data.email, data.usage, session=session)
        code = await self.generate_otp_code(email=data.email, session=session)
        payload = data.model_dump()
        payload.update({
            "code": code, 
            "status": OTPStatus.PENDING,
        })
        otp = await self.otp_repo.create_otp(payload, session=session)
        return OTPInternal.model_validate(otp)

    async def generate_otp_code(self, email: str, max_attempts: int = 10, session = None) -> str:
        for _ in range(max_attempts):
            code = generate_random_code()
            exists = await self.otp_repo.get_otp(email=email, code=code, session=session)
            if exists is None:
                return code
        raise SuspiciousOTPActivityException()

    def is_expired(self, otp: OTPInternal) -> bool:
        if otp.expires_at < datetime.now(timezone.utc):
            return True
        return False

    async def verify_otp(self, code: str, session = None) -> OTPInternal:
        """Verifies OTP code. Raises InvalidOTPException if the otp is expired, used before or not found."""
        
        otp = await self.get_otp(code=code, session=session)
        if self.is_expired(otp):
            raise OTPExpiredException()
        if otp.status != OTPStatus.PENDING:
            raise OTPAlreadyUsedException()
        
        await self.otp_repo.update_otp_status(
            email=otp.email, 
            code=code, 
            new_status=OTPStatus.VERIFIED, 
            session=session
        )
        return OTPInternal.model_validate(otp)

    async def revoke_otps(self, email: str, usage: Optional[OTPUsage] = None, session = None) -> None:
        await self.otp_repo.revoke_otps(email, usage, session=session)
    

