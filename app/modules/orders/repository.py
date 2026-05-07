import re
from typing import Any

from beanie import PydanticObjectId

from app.modules.orders.models import Order, OrderCounter


class OrderRepository:

    def _build_match_filter(
        self, user_id: PydanticObjectId, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        filters = filters or {}
        match_filter: dict[str, Any] = {"user_id": user_id}
        if filters.get("status") is not None:
            match_filter["status"] = filters["status"]
        if filters.get("is_read") is not None:
            match_filter["is_read"] = filters["is_read"]
        if filters.get("source") is not None:
            match_filter["source"] = filters["source"]
        if filters.get("customer_id") is not None:
            match_filter["customer.id"] = filters["customer_id"]
        if filters.get("item_id") is not None:
            match_filter["items.id"] = filters["item_id"]
        if filters.get("delivery_status") is not None:
            match_filter["delivery_status"] = filters["delivery_status"]
        if filters.get("payment_status") is not None:
            match_filter["payment.status"] = filters["payment_status"]
        if filters.get("order_number") is not None:
            match_filter["order_number"] = {
                "$regex": re.escape(filters["order_number"]),
                "$options": "i",
            }
        return match_filter

    def _deserialize_order(self, raw: dict[str, Any]) -> Order:
        return Order.model_validate(raw)

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
        match_filter = self._build_match_filter(user_id=user_id, filters=filters)
        # Count on the raw collection — no join needed, hits the index directly.
        total = await Order.get_pymongo_collection().count_documents(
            match_filter, session=session
        )
        orders = await Order.find(match_filter, session=session).sort(-Order.created_at).skip(skip).limit(limit).to_list()
        return total, orders

    async def count_unread(self, user_id: PydanticObjectId, session=None) -> int:
        return await Order.find(
            Order.user_id == user_id,
            Order.is_read == False,
            session=session,
        ).count()

    async def next_order_number(
        self, user_id: PydanticObjectId, session=None
    ) -> int:
        """Return the next reference number for a store's orders.

        Delegates to the ``OrderCounter`` collection via an atomic
        ``find_one_and_update`` with ``$inc`` + ``upsert``.  A single atomic
        write means concurrent order creation never produces duplicate numbers,
        with no application-level locking or transactions required.
        """
        result = await OrderCounter.get_pymongo_collection().find_one_and_update(
            {"_id": user_id},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True,
            session=session,
        )
        return result["seq"]

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
