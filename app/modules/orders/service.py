from typing import Any
from beanie import PydanticObjectId

from app.core.context import SessionContext
from app.core.enums import OrderStatus, RecordSource
from app.modules.customers.service import CustomerService
from app.modules.orders.exceptions import ItemNotBelongToUserException, OrderNotFoundException
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    OrderCreate,
    OrderCreatePublic,
    OrderFilters,
    OrderInternal,
    OrderUpdate,
)
from app.modules.orders.schemas.requests import OrderItemInput, OrderItemInputPublic
from app.modules.orders.schemas.responses import OrderResponse
from app.modules.items.service import ItemService
from app.modules.items.exceptions import ItemNotFoundException

class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        customer_service: CustomerService,
        item_service: ItemService,
    ) -> None:
        self._repo = order_repo
        self._customer_service = customer_service
        self._item_service = item_service

    # Helper methods
    def _to_response(self, order) -> OrderResponse:
        return OrderResponse.model_validate(order)

    def _to_internal(self, order) -> OrderInternal:
        return OrderInternal.model_validate(order)

    async def _resolve_items(
        self, 
        user_id: PydanticObjectId, 
        item_inputs: list[OrderItemInput | OrderItemInputPublic], 
        visible_only: bool = True,
    ) -> list[dict[str, Any]]:
        resolved = []
        for item_input in item_inputs:
            db_item = await self._item_service.get_by_id(user_id, item_input.id)
            if visible_only and not db_item.is_visible:
                raise ItemNotFoundException()
            price = item_input.price if isinstance(item_input, OrderItemInput) else db_item.price
            subtotal = item_input.quantity * price
            resolved.append({
                "id": db_item.id,
                "name": db_item.name,
                "quantity": item_input.quantity,
                "price": round(price, 2),
                "subtotal": round(subtotal, 2),
                "type": db_item.type,
                "thumbnail": db_item.thumbnail.model_dump() if db_item.thumbnail else None,
            })
        return resolved

    # -----------------------------------------------------------------
    # Owner-scoped
    # -----------------------------------------------------------------

    async def get_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        return self._to_response(order)

    async def get_own_list(
        self,
        current_user: SessionContext,
        skip: int = 0,
        limit: int = 10,
        filters: OrderFilters | None = None,
    ) -> tuple[int, list[OrderResponse]]:
        filter_dict = filters.model_dump(exclude_none=True) if filters else None
        total, orders = await self._repo.get_list(
            user_id=current_user.user.id,
            skip=skip,
            limit=limit,
            filters=filter_dict,
        )
        return total, [self._to_response(o) for o in orders]

    async def get_unread_count(self, current_user: SessionContext) -> int:
        return await self._repo.count_unread(current_user.user.id)

    async def create(
        self, current_user: SessionContext, payload: OrderCreate, session=None
    ) -> OrderResponse:
        
        data = payload.model_dump(exclude={"items", "customer_id"})
        
        items = await self._resolve_items(current_user.user.id, payload.items, visible_only=False)
        customer = await self._customer_service.get_own_by_id(current_user, payload.customer_id)
        order_number = await self._repo.next_order_number(current_user.user.id, session=session)
        
        data["items"] = items
        data["customer"] = customer.model_dump()
        data["user_id"] = current_user.user.id
        data["source"] = RecordSource.INTERNAL
        data["is_read"] = True
        data["order_number"] = f"{order_number:06d}"
        order = await self._repo.create(data, session=session)
        return self._to_response(order)

    async def update_own_by_id(
        self,
        current_user: SessionContext,
        id: PydanticObjectId,
        payload: OrderUpdate,
        session=None,
    ) -> OrderResponse:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()

        update_data = payload.model_dump(exclude_unset=True, exclude={"items"})
        if payload.items is not None:
            items = await self._resolve_items(current_user.user.id, payload.items, visible_only=False)
            update_data["items"] = items
        # No need to handle customer update, it's not allowed

        updated = await self._repo.update_by_id(current_user.user.id, id, update_data, session=session)
        return self._to_response(updated)

    async def delete_own_by_id(
        self, current_user: SessionContext, id: PydanticObjectId, session=None
    ) -> None:
        order = await self._repo.get_by_id(current_user.user.id, id)
        if not order:
            raise OrderNotFoundException()
        await self._repo.delete_by_id(current_user.user.id, id, session=session)

    # -----------------------------------------------------------------
    # Internal — used by other services (e.g. public order submission)
    # -----------------------------------------------------------------

    async def create_public_order(
        self,
        user_id: PydanticObjectId,
        payload: OrderCreatePublic,
        session=None,
    ) -> None:

        data = payload.model_dump(exclude={"items", "customer"})
        
        items = await self._resolve_items(user_id, payload.items, visible_only=True)
        
        customer = await self._customer_service.get_by_phone(user_id, payload.customer.phone)
        if not customer:
            customer = await self._customer_service.create_public_customer(
                user_id, 
                payload.customer, 
                session=session
            )

        data["items"] = items
        data["user_id"] = user_id
        data["customer"] = customer.model_dump()
        data["source"] = RecordSource.WEB
        data["status"] = OrderStatus.NEW
        data["is_read"] = False
        order_number = await self._repo.next_order_number(user_id, session=session)
        data["order_number"] = f"{order_number:06d}"
        await self._repo.create(data, session=session)
