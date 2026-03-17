from fastapi import Depends
from typing import Annotated

from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.shared.dependencies.email import EmailService, get_email_service
from app.modules.auth.tokens.dependencies import TokenService, get_token_service
from app.modules.storage.dependencies import StorageService, get_storage_service

def get_user_repository() -> UserRepository:
    """Returns user repository dependency."""
    return UserRepository()

def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> UserService:
    """Returns user service dependency."""
    return UserService(user_repo, token_service, email_service, storage_service)
