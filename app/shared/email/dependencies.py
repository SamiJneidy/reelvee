from functools import lru_cache
from fastapi import Depends
from app.core.config import settings
from app.shared.email.adapters.fastmail import FastMailEmailService
from app.shared.email.adapters.resend import ResendEmailService
from app.shared.email.adapters.ses import SESEmailService
from app.shared.email.port import EmailService

_ses_client = None


def init_ses_client(client) -> None:
    """Call once from the application lifespan with the live SES client."""
    global _ses_client
    _ses_client = client


@lru_cache
def get_ses_email_service() -> SESEmailService:
    return SESEmailService(_ses_client)


@lru_cache
def get_fastmail_email_service() -> FastMailEmailService:
    return FastMailEmailService()


@lru_cache
def get_resend_email_service() -> ResendEmailService:
    return ResendEmailService()


@lru_cache
def get_email_service(
    ses_email_service: SESEmailService = Depends(get_ses_email_service),
    fastmail_email_service: FastMailEmailService = Depends(get_fastmail_email_service),
    resend_email_service: ResendEmailService = Depends(get_resend_email_service),
) -> EmailService:
    providers: dict[str, EmailService] = {
        "ses": ses_email_service,
        "fastmail": fastmail_email_service,
        "resend": resend_email_service,
    }
    return providers[settings.current_email_provider]
