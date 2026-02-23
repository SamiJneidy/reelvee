from fastapi import Depends
from typing import Annotated
from .repository import OTPRepository
from .service import OTPService

def get_otp_repository() -> OTPRepository:
    return OTPRepository()


def get_otp_service(
    otp_repo: Annotated[OTPRepository, Depends(get_otp_repository)],
) -> OTPService:
    return OTPService(otp_repo)
