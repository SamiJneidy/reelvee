import asyncio

from app.core.config import settings
from app.shared.email.exceptions import EmailCouldNotBeSentException
from app.shared.email.port import EmailService
from app.shared.email.templates import (
    email_change_template,
    email_verification_otp_template,
    onboarding_template,
    password_reset_template,
    welcome_template
)

class SESEmailService(EmailService):
    """Concrete email implementation backed by Amazon SES (aioboto3)."""

    def __init__(self, ses_client) -> None:
        self._client = ses_client
        self._sender = settings.mail_from

    async def _send(self, to: list[str], subject: str, body: str, retries: int = 3) -> None:
        for attempt in range(retries):
            try:
                await self._client.send_email(
                    Source=self._sender,
                    Destination={"ToAddresses": to},
                    Message={
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": {"Html": {"Data": body, "Charset": "UTF-8"}},
                    },
                )
                return
            except Exception:
                raise
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
