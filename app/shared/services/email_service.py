import asyncio
from fastapi_mail import FastMail, MessageSchema
from pydantic import EmailStr
from app.core.config import mail_config
from app.shared.exceptions import EmailCouldNotBeSentException


class EmailService:
    def __init__(self):
        self.fastmail = FastMail(mail_config)


    async def send_email(self, to: list[EmailStr], subject: str, body: str, retries: int = 3, subtype: str = "plain") -> None:
        """Send an email for a list of emails."""
        for _ in range(retries):
            try:
                message = MessageSchema(
                    subject=subject, body=body, recipients=to, subtype=subtype
                )
                await self.fastmail.send_message(message)
                break
            except Exception as e:
                if _ == retries - 1:
                    raise EmailCouldNotBeSentException(detail=f"Email could not be sent after {retries} retries")
                await asyncio.sleep(1)
    
    async def send_email_verification_otp(self, email: str, code: str) -> None:
        await self.send_email(
            to=[email],
            subject="Verify your email",
            body=f"Please use this code to verify your email: {code}. Don't share this code with anyone.",
        )

    async def send_password_reset_link(self, email: str, link: str) -> None:
        await self.send_email(
            to=[email],
            subject="Reset your password",
            body=f"Please click the link below to reset your password: {link}. If you did not request a password reset, please ignore this email.",
        )

    async def send_email_change_link(self, email: str, link: str) -> None:
        body = f"""
        <p>Hello,</p>
        <p>You are receiving this email because you have requested to change your email address to this email.</p>
        <p>Please click the link below to confirm the email change:</p>
        <p><a href="{link}">Click here to confirm email change</a></p>
        <p>Or copy and paste the link below into your browser:</p>
        <p>{link}</p>
        <p>If you did not request an email change, please ignore this email.</p>
        <p>Thank you,</p>
        <p>Reelvee Team</p>
        """
        await self.send_email(to=[email], subject="Change your email", body=body, subtype="html")