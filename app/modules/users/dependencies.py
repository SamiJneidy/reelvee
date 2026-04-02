from fastapi import Depends
from typing import Annotated

from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService
from app.shared.dependencies.email import EmailService, get_email_service
from app.modules.auth.tokens.dependencies import TokenService, get_token_service
from app.modules.store.dependencies import StoreService, get_store_service


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    store_service: Annotated[StoreService, Depends(get_store_service)],
) -> UserService:
    return UserService(user_repo, token_service, email_service, store_service)
