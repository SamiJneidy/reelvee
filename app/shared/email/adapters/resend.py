import asyncio

import httpx

from app.core.config import settings
from app.shared.email.exceptions import EmailCouldNotBeSentException
from app.shared.email.port import EmailService
from app.shared.email.templates import (
    SUBJECT_EMAIL_CHANGE,
    SUBJECT_EMAIL_VERIFICATION,
    SUBJECT_ONBOARDING,
    SUBJECT_PASSWORD_RESET,
    SUBJECT_WELCOME,
    email_change_template,
    email_verification_otp_template,
    onboarding_template,
    password_reset_template,
    welcome_template,
)

_RESEND_EMAILS_URL = "https://api.resend.com/emails"


class ResendEmailService(EmailService):
    """Concrete email implementation backed by the Resend API (httpx async)."""

    def __init__(self) -> None:
        self._sender = f"{settings.mail_sender_name} <{settings.mail_from}>"
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    async def _send(self, to: list[str], subject: str, body: str, retries: int = 3) -> None:
        payload = {"from": self._sender, "to": to, "subject": subject, "html": body}
        for attempt in range(retries):
            try:
                response = await self._client.post(_RESEND_EMAILS_URL, json=payload)
                response.raise_for_status()
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
            subject=SUBJECT_WELCOME,
            body=welcome_template(email),
        )

    async def send_onboarding_email(
        self, email: str, *, first_name: str | None, store_url: str
    ) -> None:
        store_url = store_url.strip().lower()
        store_public_url = f"{settings.frontend_url.rstrip('/')}/@{store_url}"
        await self._send(
            to=[email],
            subject=SUBJECT_ONBOARDING,
            body=onboarding_template(email, first_name, store_public_url),
        )

    async def send_email_verification_otp(self, email: str, code: str) -> None:
        await self._send(
            to=[email],
            subject=SUBJECT_EMAIL_VERIFICATION,
            body=email_verification_otp_template(code),
        )

    async def send_password_reset_link(self, email: str, link: str) -> None:
        await self._send(
            to=[email],
            subject=SUBJECT_PASSWORD_RESET,
            body=password_reset_template(link),
        )

    async def send_email_change_link(self, email: str, link: str) -> None:
        await self._send(
            to=[email],
            subject=SUBJECT_EMAIL_CHANGE,
            body=email_change_template(link),
        )
