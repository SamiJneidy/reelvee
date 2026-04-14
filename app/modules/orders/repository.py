from typing import Any

from beanie import PydanticObjectId

from app.modules.orders.models import Order, OrderCounter


class OrderRepository:

    def _build_filter_list(
        self, filters: dict[str, Any] | None = None
    ) -> list:
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
        if filters.get("reference_number") is not None:
            filters_list.append(Order.reference_number == filters["reference_number"])
        return filters_list

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

    async def get_by_id_with_relations(
        self, user_id: PydanticObjectId, id: PydanticObjectId, session=None
    ) -> Order | None:
        pipeline = [
            {"$match": {"user_id": user_id, "_id": id}},
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "customer_id",
                    "foreignField": "_id",
                    "as": "customer",
                }
            },
            {
                "$lookup": {
                    "from": "items",
                    "localField": "item_id",
                    "foreignField": "_id",
                    "as": "item",
                }
            },
            {"$unwind": {"path": "$item", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
        ]
        cursor = Order.get_pymongo_collection().aggregate(pipeline, session=session)
        raw = await cursor.to_list(length=1)
        if not raw:
            return None
        return self._deserialize_order(raw[0])

    async def get_list(
        self,
        user_id: PydanticObjectId,
        skip: int = 0,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
        session=None,
    ) -> tuple[int, list[Order]]:
        filters_list = self._build_filter_list(filters)
        filters_list.append(Order.user_id == user_id)
        # Count on the raw collection — no join needed, hits the index directly.
        total = await Order.find(*filters_list, session=session).count()

        # Paginate first, then join — $lookup only runs on the page (e.g. 10
        # docs) instead of all matching orders.
        pipeline = [
            {"$match": filters},
            {"$sort": {"created_at": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer",
            }},
            {"$lookup": {
                "from": "items",
                "localField": "item_id",
                "foreignField": "_id",
                "as": "item",
            }},
            {"$unwind": {"path": "$item", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
        ]
        # Beanie's aggregate() wrapper tries to await Motor's aggregate cursor,
        # which is not a coroutine in Motor 3.x. Use Motor directly instead:
        # collection.aggregate() returns a cursor synchronously, and its
        # .to_list() is the awaitable part.
        cursor = Order.get_pymongo_collection().aggregate(pipeline)
        raw_orders = await cursor.to_list(length=None)
        orders = [self._deserialize_order(raw) for raw in raw_orders]
        return total, orders

    async def count_unread(self, user_id: PydanticObjectId, session=None) -> int:
        return await Order.find(
            Order.user_id == user_id,
            Order.is_read == False,
            session=session,
        ).count()

    async def next_reference_number(
        self, user_id: PydanticObjectId, session=None
    ) -> int:
        """Return the next reference number for a store's orders.

        Delegates to the ``OrderCounter`` collection via an atomic
        ``find_one_and_update`` with ``$inc`` + ``upsert``.  A single atomic
        write means concurrent order creation never produces duplicate numbers,
        with no application-level locking or transactions required.
        """
        result = await OrderCounter.get_motor_collection().find_one_and_update(
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
        return await self.get_by_id_with_relations(order.user_id, order.id, session=session)

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
        return await self.get_by_id_with_relations(order.user_id, order.id, session=session)

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
