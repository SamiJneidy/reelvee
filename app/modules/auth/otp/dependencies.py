from fastapi import Depends
from typing import Annotated
from .repository import OTPRepository
from .service import OTPService
from app.shared.dependencies.email import EmailService, get_email_service

def get_otp_repository() -> OTPRepository:
    return OTPRepository()


def get_otp_service(
    otp_repo: Annotated[OTPRepository, Depends(get_otp_repository)],
    email_service: EmailService = Depends(get_email_service),
) -> OTPService:
    return OTPService(otp_repo, email_service)
