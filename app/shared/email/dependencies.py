from fastapi import Depends
from app.shared.email.service import EmailService

def get_email_service() -> EmailService:
    return EmailService()