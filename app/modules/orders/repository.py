from typing import Any

from beanie import PydanticObjectId

from app.modules.orders.models import Order


class OrderRepository:

    def _build_filters(self, filters: dict[str, Any] | None = None) -> list:
        filters = filters or {}
        filters_list = []
        if filters.get("status") is not None:
            filters_list.append(Order.status == filters["status"])
        if filters.get("is_read") is not None:
            filters_list.append(Order.is_read == filters["is_read"])
        if filters.get("source") is not None:
            filters_list.append(Order.source == filters["source"])
        if filters.get("customer_id") is not None:
            filters_list.append(Order.customer_id == filters["customer_id"])
        if filters.get("item_id") is not None:
            filters_list.append(Order.item_id == filters["item_id"])
        if filters.get("delivery_status") is not None:
            filters_list.append(Order.delivery_status == filters["delivery_status"])
        return filters_list

    async def get_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> Order | None:
        return await Order.find_one(
            Order.user_id == user_id,
            Order.id == id,
            session=session,
        )

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Order]]:
        filters_list = self._build_filters(filters)
        filters_list.append(Order.user_id == user_id)
        query = Order.find(*filters_list, session=session)
        total = await query.count()
        orders = await query.sort(-Order.created_at).skip(skip).limit(limit).to_list()
        return total, orders

    async def count_unread(self, user_id: PydanticObjectId, session=None) -> int:
        return await Order.find(
            Order.user_id == user_id,
            Order.is_read == False,
            session=session,
        ).count()

    async def create(self, data: dict[str, Any], session=None) -> Order:
        order = Order(**data)
        await order.insert(session=session)
        return order

    async def update_by_id(
        self,
        user_id: PydanticObjectId,
        id: PydanticObjectId,
        data: dict[str, Any],
        session=None,
    ) -> Order | None:
        order = await Order.find_one(
            Order.user_id == user_id,
            Order.id == id,
            session=session,
        )
        if order is None:
            return None
        for key, value in data.items():
            if hasattr(Order, key):
                setattr(order, key, value)
        await order.save(session=session)
        return order

    async def delete_by_id(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> None:
        order = await Order.find_one(
            Order.user_id == user_id,
            Order.id == id,
            session=session,
        )
        if order is not None:
            await order.delete(session=session)
