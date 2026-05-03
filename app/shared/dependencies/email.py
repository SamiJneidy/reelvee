from app.shared.services.email.adapters.fastmail import FastMailEmailService
from app.shared.services.email.port import EmailService


def get_email_service() -> EmailService:
    return FastMailEmailService()
