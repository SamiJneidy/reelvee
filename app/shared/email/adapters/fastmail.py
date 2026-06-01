import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import settings
from app.shared.email.exceptions import EmailCouldNotBeSentException
from app.shared.email.port import EmailService

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)
from app.shared.email.templates import (
    email_change_template,
    email_verification_otp_template,
    onboarding_template,
    password_reset_template,
    welcome_template,
)


class FastMailEmailService(EmailService):
    """Concrete email implementation backed by fastapi-mail / SMTP."""

    def __init__(self) -> None:
        self._fastmail = FastMail(mail_config)

    async def _send(self, to: list[str], subject: str, body: str, retries: int = 3) -> None:
        for attempt in range(retries):
            try:
                message = MessageSchema(
                    subject=subject,
                    body=body,
                    recipients=to,
                    subtype="html",
                )
                await self._fastmail.send_message(message)
                return
            except Exception:
                if attempt == retries - 1:
                    raise EmailCouldNotBeSentException(
                        detail=f"Email could not be sent after {retries} retries"
                    )
                await asyncio.sleep(1)

    async def send_welcome_email(self, email: str) -> None:
        await self._send(
            to=[email],
            subject="Welcome to Reelvee — verify your email next",
            body=welcome_template(email),
        )

    async def send_onboarding_email(
        self, email: str, *, first_name: str | None, store_url: str
    ) -> None:
        store_url = store_url.strip().lower()
        store_public_url = f"{settings.frontend_url.rstrip('/')}/@{store_url}"
        await self._send(
            to=[email],
            subject="Your Storelink store is ready",
            body=onboarding_template(email, first_name, store_public_url),
        )

    async def send_email_verification_otp(self, email: str, code: str) -> None:
        await self._send(
            to=[email],
            subject="Verify your email address",
            body=email_verification_otp_template(code),
        )

    async def send_password_reset_link(self, email: str, link: str) -> None:
        await self._send(
            to=[email],
            subject="Reset your password",
            body=password_reset_template(link),
        )

    async def send_email_change_link(self, email: str, link: str) -> None:
        await self._send(
            to=[email],
            subject="Confirm your email change",
            body=email_change_template(link),
        )
