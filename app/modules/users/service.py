from datetime import datetime, timezone
import re
from typing import Any

from fastapi import status
from pymongo.errors import DuplicateKeyError
from beanie.exceptions import RevisionIdWasChanged

from app.core.config import settings
from app.core.enums import TokenScope, UserStatus, UserStep
from app.core.exceptions.exceptions import DuplicateKeyErrorException
from app.core.security import verify_password
from app.modules.auth.tokens.schemas import EmailChangeToken
from app.modules.auth.tokens.service import TokenService
from app.modules.users.exceptions import (
    EmailChangeNotAllowedException,
    InvalidStoreLinkException,
    UserAlreadyCompletedException,
    UserAlreadyExistsException,
    UserNotFoundException,
    UserNotVerifiedException,
)
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserFilters,
    UserInDB,
    UserInternal,
    UserCreate,
    UserUpdateInternal,
)
from app.modules.users.schemas.requests import ChangeEmailRequest, RequestEmailChangeRequest, SignUpCompleteRequest
from app.modules.users.schemas.responses import SignUpCompleteResponse, UserResponse
from app.shared.services import EmailService

class UserService:
    def __init__(self, 
        user_repo: UserRepository, 
        token_service: TokenService,
        email_service: EmailService
    ) -> None:
        self._repo = user_repo
        self._token_service = token_service
        self._email_service = email_service

    async def get_by_id_in_db(self, id: str) -> UserInDB:
        user = await self._repo.get_by_id(id)
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_by_email_in_db(self, email: str) -> UserInDB:
        user = await self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        return UserInDB.model_validate(user)

    async def get_by_id(self, id: str) -> UserInternal:
        user = await self._repo.get_by_id(id)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def get_by_email(self, email: str) -> UserInternal:
        user = await self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def get_by_store_url(self, store_url: str) -> UserInternal:
        user = await self._repo.get_by_store_url(store_url)
        if not user:
            raise UserNotFoundException()
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

    async def sign_up_complete(
        self, email: str, data: SignUpCompleteRequest, session = None
    ) -> SignUpCompleteResponse:
        user = await self.get_by_email(email)
        if not user.is_email_verified:
            raise UserNotVerifiedException()
        if user.is_completed:
            raise UserAlreadyCompletedException()
        user_data = UserUpdateInternal(
            **data.model_dump(),
            status=UserStatus.ACTIVE,
            step=UserStep.TWO,
            is_completed=True,
            is_deleted=False,
            last_login=datetime.now(timezone.utc),
            invalid_login_attempts=0,
        )
        try:
            full_user = await self.update_by_email(email, user_data, session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise DuplicateKeyErrorException("Duplicate key error. The store link or whatsapp number is already in use")
        return SignUpCompleteResponse(user=UserResponse.model_validate(full_user))

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
        try:
            user = await self._repo.update_by_email(email, update_data, session=session)
        except (DuplicateKeyError, RevisionIdWasChanged):
            raise DuplicateKeyErrorException("Duplicate key error. Some of the fields are already in use (email, store link, whatsapp number)")
        if not user:
            raise UserNotFoundException()
        return UserInternal.model_validate(user)

    async def request_email_change(
        self, user_id: str, data: RequestEmailChangeRequest, session = None
    ) -> None:
        user = await self.get_by_id_in_db(user_id)
        if not verify_password(data.password, user.password):
            raise EmailChangeNotAllowedException(detail="Incorrect password")
        payload = EmailChangeToken(
            scope=TokenScope.EMAIL_CHANGE,
            sub=user_id,
            current_email=user.email,
            new_email=data.new_email,
        )
        change_token = self._token_service.generate_email_change_token(payload)
        change_url = f"{settings.frontend_url}/change-email?token={change_token}"
        await self._email_service.send_email_change_link(data.new_email, change_url)

    async def confirm_email_change(
        self, data: ChangeEmailRequest, session = None
    ) -> UserInternal:
        token_payload = self._token_service.decode_token(data.token)
        token = EmailChangeToken.model_validate(token_payload)
        if token.scope != TokenScope.EMAIL_CHANGE:
            raise EmailChangeNotAllowedException("Invalid Token")
        user = await self.get_by_id(token.sub)
        if user.email != token.current_email:
            raise EmailChangeNotAllowedException("Invalid Token. Mismatch!")
        updated_user = await self.update_by_email(token.current_email, {"email": token.new_email}, session)
        return UserInternal.model_validate(updated_user)

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
        user = await self.get_by_email(email)
        await self._repo.delete_by_email(email, session=session)
        return UserInternal.model_validate(user)
