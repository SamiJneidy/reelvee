import re
from datetime import datetime
from typing import Any

from beanie import PydanticObjectId

from app.core.enums import UserStatus
from app.modules.users.models import User


class UserRepository:
    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("status"):
            filters_list.append(User.status == filters["status"])
        if filters.get("first_name"):
            filters_list.append(
                {"first_name": {"$regex": re.escape(filters["first_name"]), "$options": "i"}}
            )
        if filters.get("last_name"):
            filters_list.append(
                {"last_name": {"$regex": re.escape(filters["last_name"]), "$options": "i"}}
            )
        if filters.get("country_code"):
            filters_list.append(
                {"country_code": {"$regex": re.escape(filters["country_code"]), "$options": "i"}}
            )
        if filters.get("email"):
            filters_list.append(
                {"email": {"$regex": re.escape(filters["email"]), "$options": "i"}}
            )
        if filters.get("whatsapp_number"):
            filters_list.append(
                {"whatsapp_number": {"$regex": re.escape(filters["whatsapp_number"]), "$options": "i"}}
            )
        if filters.get("business_name"):
            filters_list.append(
                {"business_name": {"$regex": re.escape(filters["business_name"]), "$options": "i"}}
            )
        if filters.get("store_url"):
            filters_list.append(
                {"store_url": {"$regex": re.escape(filters["store_url"]), "$options": "i"}}
            )

    async def get_by_id(self, id: PydanticObjectId, session=None) -> User | None:
        return await User.get(id, session=session)

    async def get_by_email(self, email: str, session=None) -> User | None:
        return await User.find_one(User.email == email.lower().strip(), session=session)

    async def get_by_store_url(self, store_url: str, session=None) -> User | None:
        return await User.find_one(User.store_url == store_url.lower().strip(), session=session)

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[User]]:
        filters_list = self._build_filters(filters)
        query = User.find(*filters_list, session=session)
        total = await query.count()
        users = await query.skip(skip).limit(limit).to_list()
        return total, users

    async def create(self, data: dict[str, Any], session=None) -> User:
        if "email" in data:
            data = {**data, "email": data["email"].lower().strip()}
        user = User(**data)
        await user.insert(session=session)
        return user

    async def update_by_id(self, id: PydanticObjectId, data: dict[str, Any], session=None) -> User | None:
        user = await User.get(id, session=session)
        if user is None:
            return None
        for key, value in data.items():
            if hasattr(User, key):
                setattr(user, key, value)
        await user.save(session=session)
        return user

    async def update_by_email(self, email: str, data: dict[str, Any], session=None) -> User | None:
        user = await self.get_by_email(email, session=session)
        if user is None:
            return None
        for key, value in data.items():
            if hasattr(User, key):
                setattr(user, key, value)
        await user.save(session=session)
        return user

    async def increment_invalid_login_attempts(self, email: str, session=None) -> User | None:
        user = await self.get_by_email(email, session=session)
        if user is None:
            return None
        user.invalid_login_attempts += 1
        await user.save(session=session)
        return user

    async def reset_invalid_login_attempts(self, email: str, session=None) -> User | None:
        user = await self.get_by_email(email, session=session)
        if user is None:
            return None
        await user.set({User.invalid_login_attempts: 0}, session=session)
        return user

    async def update_status(self, email: str, status: UserStatus, session=None) -> User | None:
        user = await self.get_by_email(email, session=session)
        if user is None:
            return None
        await user.set({User.status: status}, session=session)
        return user

    async def update_last_login(self, email: str, last_login: datetime, session=None) -> User | None:
        user = await self.get_by_email(email, session=session)
        if user is None:
            return None
        await user.set({User.last_login: last_login}, session=session)
        return user

    async def delete_by_email(self, email: str, session=None) -> None:
        user = await self.get_by_email(email, session=session)
        if user is not None:
            await user.delete(session=session)
