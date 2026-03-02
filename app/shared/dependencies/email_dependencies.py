from fastapi import Depends
from app.shared.services.email_service import EmailService

def get_email_service() -> EmailService:
    return EmailService()