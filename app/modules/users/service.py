"""User service: application logic for user operations."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.core.enums import UserStatus
from app.modules.users.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserFilters,
    UserInDB,
    UserResponse,
    UserSignUp,
    UserUpdate,
)

class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def _get_or_raise(self, id: str, email: str) -> UserInDB:
        user = await self._repo.get_by_id(id) or await self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_user_in_db(self, email: str) -> UserInDB:
        user = await self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_by_id(self, id: str) -> UserResponse:
        user = await self._get_or_raise(id=id)
        return UserResponse.model_validate(user)

    async def get_by_email(self, email: str) -> UserResponse:
        user = await self._get_or_raise(email=email)
        return UserResponse.model_validate(user)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: UserFilters | None = None,
    ) -> tuple[int, list[UserResponse]]:
        total, users = await self._repo.get_users(
            skip=skip,
            limit=limit,
            filters=filters,
        )
        return total, [UserResponse.model_validate(u) for u in users]

    async def create_user(self, payload: UserSignUp, session=None) -> UserResponse:
        existing = await self._repo.get_by_email(payload.email)
        if existing:
            raise UserAlreadyExistsException()
        data = payload.model_dump()
        user = await self._repo.create(data, session=session)
        return UserResponse.model_validate(user)

    async def update_by_email(
        self,
        email: str,
        update_data: UserUpdate | dict[str, Any],
        session=None,
    ) -> UserResponse:
        if isinstance(update_data, UserUpdate):
            update_data = update_data.model_dump(exclude_none=True)
        user = await self._repo.update_by_email(email, update_data, session=session)
        if not user:
            raise UserNotFoundException()
        return UserResponse.model_validate(user)

    async def increment_invalid_login_attempts(self, email: str, session=None) -> UserResponse:
        user = await self._repo.increment_invalid_login_attempts(email, session=session)
        if not user:
            raise UserNotFoundException()
        return UserResponse.model_validate(user)

    async def reset_invalid_login_attempts(self, email: str, session=None) -> UserResponse:
        user = await self._repo.reset_invalid_login_attempts(email, session=session)
        if not user:
            raise UserNotFoundException()
        return UserResponse.model_validate(user)

    async def update_user_status(self, email: str, status: UserStatus, session=None) -> UserResponse:
        user = await self._repo.update_status(email, status, session=session)
        if not user:
            raise UserNotFoundException()
        return UserResponse.model_validate(user)

    async def update_last_login(
        self,
        email: str,
        last_login: datetime,
        session=None,
    ) -> UserResponse:
        user = await self._repo.update_last_login(email, last_login, session=session)
        if not user:
            raise UserNotFoundException()
        return UserResponse.model_validate(user)

    async def delete_user(self, email: str, session=None) -> UserResponse:
        user = await self._get_or_raise(email=email, session=session)
        await self._repo.delete_by_email(email, session=session)
        return UserResponse.model_validate(user)
