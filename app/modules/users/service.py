"""User service: application logic for user operations."""

from __future__ import annotations

from datetime import datetime
import re
from typing import TYPE_CHECKING, Any

from fastapi import status

from app.core.config import settings
from app.core.enums import UserStatus
from app.modules.users.exceptions import (
    InvalidStoreLinkException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserFilters,
    UserInDB,
    UserInternal,
    UserCreate,
    UserUpdateInternal,
)

class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def _get_or_raise(self, id: str | None = None, email: str | None = None) -> UserInDB:
        if id:
            user = await self._repo.get_by_id(id)
        elif email:
            user = await self._repo.get_by_email(email)
        else:
            raise UserNotFoundException()
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_user_in_db(self, email: str) -> UserInDB:
        user = await self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_by_id(self, id: str) -> UserInternal:
        user = await self._get_or_raise(id=id)
        return UserInternal.model_validate(user)

    async def get_by_email(self, email: str) -> UserInternal:
        user = await self._get_or_raise(email=email)
        return UserInternal.model_validate(user)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: UserFilters | None = None,
    ) -> tuple[int, list[UserInternal]]:
        total, users = await self._repo.get_users(
            skip=skip,
            limit=limit,
            filters=filters,
        )
        return total, [UserInternal.model_validate(u) for u in users]

    async def validate_store_link(self, user_email: str, store_url: str, session=None) -> None:
        if len(store_url) < 3:
            raise InvalidStoreLinkException("Store link must be at least 3 characters long")
        store_url = store_url.strip().lower()
        regex = re.compile(r'^[a-z0-9-]+$')
        if not regex.match(store_url):
            raise InvalidStoreLinkException("Store link can only contain letters, numbers and hyphens")
        existing = await self._repo.get_by_store_url(store_url, session)
        if existing and existing.email != user_email:
            raise InvalidStoreLinkException("Store link is already in use", status.HTTP_409_CONFLICT)

    async def create_user(self, payload: UserCreate, session=None) -> UserInternal:
        existing = await self._repo.get_by_email(payload.email)
        if existing:
            raise UserAlreadyExistsException()
        if payload.store_url:
            await self.validate_store_link(payload.email, payload.store_url, session)
        data = payload.model_dump()
        user = await self._repo.create(data, session=session)
        return UserInternal.model_validate(user)

    async def update_by_email(
        self,
        email: str,
        update_data: UserUpdateInternal | dict[str, Any],
        session=None,
    ) -> UserInternal:
        if isinstance(update_data, UserUpdateInternal):
            update_data = update_data.model_dump(exclude_none=True)
        if update_data.get("store_url"):
            await self.validate_store_link(email, update_data["store_url"], session)
        user = await self._repo.update_by_email(email, update_data, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def increment_invalid_login_attempts(self, email: str, session=None) -> UserInternal:
        user = await self._repo.increment_invalid_login_attempts(email, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def reset_invalid_login_attempts(self, email: str, session=None) -> UserInternal:
        user = await self._repo.reset_invalid_login_attempts(email, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def update_user_status(self, email: str, status: UserStatus, session=None) -> UserInternal:
        user = await self._repo.update_status(email, status, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def update_last_login(
        self,
        email: str,
        last_login: datetime,
        session=None,
    ) -> UserInternal:
        user = await self._repo.update_last_login(email, last_login, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def soft_delete_user(self, email: str, session=None) -> UserInternal:
        user = await self._repo.update_by_email(email, {"is_deleted": True}, session=session)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def delete_user(self, email: str, session=None) -> UserInternal:
        """NOT A SOFT DELETE, IT WILL DELETE THE USER FROM THE DATABASE"""
        user = await self._get_or_raise(email=email)
        await self._repo.delete_by_email(email, session=session)
        return UserInternal.model_validate(user)
