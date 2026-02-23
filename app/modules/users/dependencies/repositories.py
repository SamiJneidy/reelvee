from fastapi import Depends
from typing import Annotated

from app.modules.users.repository import UserRepository


def get_user_repository() -> UserRepository:
    """Returns user repository dependency."""
    return UserRepository()
