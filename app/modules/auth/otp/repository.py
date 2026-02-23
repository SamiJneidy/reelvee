from app.core.enums import OTPUsage, OTPStatus
from app.modules.auth.otp.models import OTP


class OTPRepository:

    async def get_otp(
        self, 
        code: str | None = None,
        email: str | None = None,
        usage: OTPUsage | None = None,
        status: OTPStatus | None = None,
        session=None,
    ) -> OTP | None:
        filters = []
        if code is not None:
            filters.append(OTP.code == code)
        if email is not None:
            filters.append(OTP.email == email)
        if usage is not None:
            filters.append(OTP.usage == usage)
        if status is not None:
            filters.append(OTP.status == status)

        if not filters:
            return None
        return await OTP.find(*filters, session=session).first_or_none()


    async def create_otp(self, data: dict, session=None) -> OTP:
        otp = OTP(**data)
        await otp.insert(session=session)
        return otp

    async def update_otp_status(self, email: str, code: str, new_status: OTPStatus, session=None) -> OTP | None:
        otp = await OTP.find_one(OTP.email == email, OTP.code == code, session=session)
        if otp is None:
            return None
        await otp.set({OTP.status: new_status}, session=session)
        return otp

    async def delete_otp(self, code: str, session=None) -> None:
        otp = await OTP.find_one(OTP.code == code, session=session)
        if otp is None:
            return None
        await otp.delete(session=session)

    async def revoke_otps(self, email: str, usage: OTPUsage | None = None, session=None) -> None:
        stmt = OTP.find(OTP.email == email, session=session)
        if usage is not None:
            stmt = stmt.find(OTP.usage == usage, session=session)
        await stmt.delete(session=session)
