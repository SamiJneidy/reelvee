import re
from typing import Any

from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.modules.customers.models import Customer


class CustomerRepository:

    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("status") is not None:
            filters_list.append(Customer.status == filters["status"])
        if filters.get("source") is not None:
            filters_list.append(Customer.source == filters["source"])
        if filters.get("is_favourite") is not None:
            filters_list.append(Customer.is_favourite == filters["is_favourite"])
        if filters.get("name"):
            filters_list.append(
                {"name": {"$regex": re.escape(filters["name"]), "$options": "i"}}
            )
        if filters.get("phone"):
            filters_list.append(
                {"phone": {"$regex": re.escape(filters["phone"]), "$options": "i"}}
            )
        if filters.get("email"):
            filters_list.append(
                {"email": {"$regex": re.escape(filters["email"]), "$options": "i"}}
            )
        return filters_list

    async def get_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> Customer | None:
        return await Customer.find_one(
            Customer.user_id == user_id,
            Customer.id == id,
            session=session,
        )

    async def get_by_phone(
        self, user_id: PydanticObjectId, phone: str, session=None
    ) -> Customer | None:
        return await Customer.find_one(
            Customer.user_id == user_id,
            Customer.phone == phone.strip(),
            session=session,
        )

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Customer]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Customer.user_id == user_id)
        query = Customer.find(*filters_list, session=session)
        total = await query.count()
        customers = await query.sort(-Customer.created_at).skip(skip).limit(limit).to_list()
        return total, customers

    async def create(self, data: dict[str, Any], session=None) -> Customer:
        customer = Customer(**data)
        await customer.insert(session=session)
        return customer

    async def update_by_id(
        self,
        user_id: PydanticObjectId,
        id: PydanticObjectId,
        data: dict[str, Any],
        session=None,
    ) -> Customer | None:
        customer = await Customer.find_one(
            Customer.user_id == user_id,
            Customer.id == id,
            session=session,
        )
        if customer is None:
            return None
        for key, value in data.items():
            if hasattr(Customer, key):
                setattr(customer, key, value)
        await customer.save(session=session)
        return customer

    async def delete_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> None:
        customer = await Customer.find_one(
            Customer.user_id == user_id,
            Customer.id == id,
            session=session,
        )
        if customer is not None:
            await customer.delete(session=session)
