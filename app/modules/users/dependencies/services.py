from fastapi import Depends
from typing import Annotated

from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService

from .repositories import get_user_repository


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """Returns user service dependency."""
    return UserService(user_repo)
